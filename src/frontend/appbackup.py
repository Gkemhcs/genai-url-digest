from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import requests,os,redis
from opentelemetry import trace, propagators, baggage
from opentelemetry.sdk.resources import  Resource
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import  BatchSpanProcessor,ConsoleSpanExporter

resource = Resource(attributes={
    "service.name": "frontend"  # Your desired service name
})

trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter(os.getenv("OTLP_ENDPOINT") or "http://localhost:4318/v1/traces")))
tracer = trace.get_tracer(__name__)

BACKEND_SERVER_URL=os.getenv("BACKEND_SERVER_URL")  or  "http://localhost:5001" 


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['SESSION_REDIS'] = redis.Redis(
    host=os.getenv("REDIS_SERVER_URL") or "localhost", 
    port=6379, 
   password=os.getenv("REDIS_AUTH_STRING") or "gkem1234",
    db=0, encoding='utf-8',
)
Session(app)

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', title="LinkDigest")

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
      with tracer.start_as_current_span("user_login") as span:  
        username = request.form['username']
        if username:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Username is required!', 'danger')
    return render_template('login.html', title="Login - LinkDigest")

@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('login'))

        with tracer.start_as_current_span("process_url") as span:
            ctx = baggage.set_baggage("username",session["username"])
            headers = {}
            W3CBaggagePropagator().inject(headers, ctx)
            TraceContextTextMapPropagator().inject(headers, ctx)
            urls = request.form.getlist('urls')
            request_body={"urls":urls,"username":session["username"]}
            print(urls)
            url=BACKEND_SERVER_URL+"/process_url"
            response=requests.post(url=url,data=request_body)
            print(response)
            return render_template("ask_question.html",title="LinkDigest", message="URLs submitted successfully")
    
@app.route("/get_answer",methods=["POST"])
def answer():
   question=request.form.get("question")
   print(request.form)
   print("question:-",question)  
   request_body={"question":question,"username":session["username"]}
   url=BACKEND_SERVER_URL+"/ask_question"
   response=requests.post(url=url,data=request_body)
   print(response.json())
   sources=response.json()["sources"]
   answer=response.json()["answer"]
   if isinstance(sources,list):
             return render_template("ask_question.html",title="LinkDigest",question=question,answer=answer,sources=sources)
 
   if sources:
       return render_template("ask_question.html",title="LinkDigest",question=question,answer=answer,source=sources)
   return render_template("ask_question.html",title="LinkDigest",question=question,answer=answer)
      
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=5000,host="0.0.0.0")
