import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, conint, confloat
from typing import Optional, Dict, Any

from database import create_document, db
from schemas import Lead as LeadSchema, DemoRequest as DemoRequestSchema

app = FastAPI(title="Contractor Smart Site API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Models for calculator input/output
class CalcInput(BaseModel):
    monthly_inquiries: conint(ge=0, le=10000) = Field(..., description="Monthly inbound inquiries")
    connection_rate: confloat(ge=0, le=100) = Field(..., description="Current connection rate (percent)")
    close_rate: confloat(ge=0, le=100) = Field(..., description="Current close rate (percent)")
    lifetime_value: confloat(gt=0, le=1000000) = Field(..., description="Customer lifetime value (USD)")


class CalcResult(BaseModel):
    current_connected: float
    current_closed: float
    current_revenue: float
    smart_connected: float
    smart_closed: float
    smart_revenue: float
    lift_revenue: float
    assumptions: Dict[str, Any]


@app.post("/api/calculate", response_model=CalcResult)
def calculate_revenue(body: CalcInput):
    # Current
    curr_conn = body.monthly_inquiries * (body.connection_rate / 100)
    curr_close = curr_conn * (body.close_rate / 100)
    curr_rev = curr_close * body.lifetime_value

    # Smart Site AI assumptions
    # Improve connection rate by +20 percentage points up to 95%
    # Improve close rate by +5 percentage points up to 85%
    smart_conn_rate = min(95.0, body.connection_rate + 20.0)
    smart_close_rate = min(85.0, body.close_rate + 5.0)

    smart_conn = body.monthly_inquiries * (smart_conn_rate / 100)
    smart_close = smart_conn * (smart_close_rate / 100)
    smart_rev = smart_close * body.lifetime_value

    return CalcResult(
        current_connected=round(curr_conn, 2),
        current_closed=round(curr_close, 2),
        current_revenue=round(curr_rev, 2),
        smart_connected=round(smart_conn, 2),
        smart_closed=round(smart_close, 2),
        smart_revenue=round(smart_rev, 2),
        lift_revenue=round(smart_rev - curr_rev, 2),
        assumptions={
            "smart_connection_rate": smart_conn_rate,
            "smart_close_rate": smart_close_rate,
        },
    )


@app.post("/api/lead")
def create_lead(lead: LeadSchema):
    try:
        lead_id = create_document("lead", lead)
        return {"status": "ok", "id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/demo")
def create_demo(req: DemoRequestSchema):
    try:
        demo_id = create_document("demorequest", req)
        # Return a simple simulated conversation transcript
        transcript = [
            {"role": "visitor", "text": req.sample_intent or "Hi! I'm looking for a quote."},
            {"role": "ai", "text": "You're in the right place! I can help with that. May I have your address and a good time for an estimate?"},
            {"role": "visitor", "text": "Tomorrow afternoon works. 123 Main St."},
            {"role": "ai", "text": "Great. I've penciled you in for 2:30 PM. You'll get a confirmation by text. Anything else I can answer now?"},
        ]
        return {"status": "ok", "id": demo_id, "transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
