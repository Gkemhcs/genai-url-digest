from flask import Flask ,request,jsonify
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_postgres.vectorstores import PGVector 
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai import VertexAI
import os
from opentelemetry import trace, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import  Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import  BatchSpanProcessor,ConsoleSpanExporter
from opentelemetry.baggage.propagation import W3CBaggagePropagator


PGVECTOR_PASSWORD=os.getenv("PGVECTOR_PASSWORD") or "gkem123"
PGVECTOR_DATABASE=os.getenv("PGVECTOR_DATABASE") or "urldigest"
PGVECTOR_USER=os.getenv("PGVECTOR_USER") or "gkem"
PGVECTOR_PORT=os.getenv("PGVECTOR_PORT") or 5432
PGVECTOR_HOST_URL=os.getenv("PGVECTOR_HOST_URL") or "localhost"
resource = Resource(attributes={
    "service.name": "urldigest_backend"  # Your desired service name
})
OTLP_ENDPOINT=os.getenv("OTLP_ENDPOINT") or "localhost"
OTLP_PORT=os.getenv("OTLP_PORT") or 4318

trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter(f"http://{OTLP_ENDPOINT}:{OTLP_PORT}/v1/traces")))
tracer = trace.get_tracer(__name__)

connection = f"postgresql+psycopg://{PGVECTOR_USER}:{PGVECTOR_PASSWORD}@{PGVECTOR_HOST_URL}:5432/{PGVECTOR_DATABASE}"

llm=VertexAI()
embeddings=VertexAIEmbeddings(model_name="textembedding-gecko")


app=Flask(__name__)

@app.route("/")
def home():
       return {"status":200,"message":"everything is working fine"}

@app.route("/process_url",methods=["POST"])
def process():
        
         
            
            headers = dict(request.headers)
            carrier ={'traceparent': headers['Traceparent']}
            ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
            b2 ={'baggage': headers['Baggage']}
            ctx2 = W3CBaggagePropagator().extract(b2, context=ctx)
            with tracer.start_span("generate_and_store_embeddings route", context=ctx2):
                    urls=baggage.get_baggage('urls', ctx2)
                    if urls:
                      urls = urls.split(',')
                      print("urltype",type(urls),"urls",urls)
                    with tracer.start_span(" load and split data", context=ctx2):
                        print(urls)
                        loader = UnstructuredURLLoader(urls=urls)
                        data = loader.load()
                        text_splitter = RecursiveCharacterTextSplitter(
                        separators=['\n\n', '\n', '.', ','],
                        chunk_size=1000
                        )
                        docs = text_splitter.split_documents(data)
                    print(docs)    
                    with tracer.start_span("create and store embeddings", context=ctx2):
                        print("username",baggage.get_baggage("username",ctx2))
                       
                        vectorstore = PGVector(
                        embeddings=embeddings,
                        collection_name=baggage.get_baggage("username",ctx2),
                        connection=connection,
                        use_jsonb=True,
                          )
                        db=vectorstore.add_documents(docs)
                        print("db",db)
                    return {"status":"ok"}
@app.route("/ask_question", methods=["POST"])
def ask_question():
        headers = dict(request.headers)
        carrier ={'traceparent': headers['Traceparent']}
        ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
        b2 ={'baggage': headers['Baggage']}
        ctx2 = W3CBaggagePropagator().extract(b2, context=ctx)
        with tracer.start_span("vector_search route", context=ctx2):
            question = baggage.get_baggage("question",ctx2)
            print(question)
            if not question:
                return jsonify({"status": 400, "message": "No question provided"}), 400
            print("username:-",baggage.get_baggage("username",ctx2))
            # Initialize PGVector for vector search
            vectorstore = PGVector(
                embeddings=embeddings,
                collection_name=baggage.get_baggage("username",ctx2),
                connection=connection,
                use_jsonb=True,
            )
            chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
            # Perform vector search
            result = chain({"question": question}, return_only_outputs=True)
            
            # Format the results
          
            sources = result.get("sources", "")
            
            if sources:
              return jsonify({"status": 200, "answer": result["answer"],"sources":sources})
      
            print(result["answer"])
            return jsonify({"status": 200, "answer": result["answer"]})

if(__name__=="__main__"):
       app.run(port=5001,host="0.0.0.0")



