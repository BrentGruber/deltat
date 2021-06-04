import logging
import time
import uvicorn
from fastapi import FastAPI, Request

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from router import router as v1_router
from config import settings


# Log formatter
class SpanFormatter(logging.Formatter):
    def format(self, record):
        trace_id = trace.get_current_span().get_span_context().trace_id
        if trace_id == 0:
            record.trace_id = None
        else:
            record.trace_id = "{trace:032x}".format(trace=trace_id)
        return super().format(record)

# Logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = SpanFormatter('time="%(asctime)s" service=%(name)s level=%(levelname)s %(message)s trace_id=%(trace_id)s')
handler.setFormatter(formatter)
log.addHandler(handler)

# Tracing
resource = Resource(attributes={
    "service.name": f"{settings.OTEL_SERVICE_NAME}"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_exporter = OTLPSpanExporter(endpoint=f"{settings.OTEL_HOST}:{settings.OTEL_PORT}", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))


# Fastapi
app = FastAPI(title=settings.PROJECT_NAME)
FastAPIInstrumentor.instrument_app(app)



app.include_router(v1_router, prefix=settings.API_V1_STR)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Adds an X-Process-Time header to response with how long the call took to execute
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def add_logs(request: Request, call_next):
    """
    Uses log formatter to log request
    """
    response = await call_next(request)
    log.error(
        'method=%s path="%s" status=%s',
        request.method,
        request.url.path,
        response.status_code,
    )
    return response

@app.middleware("http")
async def add_trace(request: Request, call_next):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(request.url.path):
        return await call_next(request)

@app.get("/tracing")
async def test_trace():
    return "Trace On"


if __name__ == "__main__":
    if settings.ENVIRONMENT.upper() == "LOCAL":
        uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, log_level=settings.LOGLEVEL, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, log_level=settings.LOGLEVEL)