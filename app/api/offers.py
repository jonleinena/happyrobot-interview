from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.core.api_key_auth import get_api_key
from app.models.call_log import CallLog
from app.schemas.carrier import CallOutcome, CallOutcomeResponse
from app.config import settings


router = APIRouter()


@router.post("/log", response_model=CallOutcomeResponse)
def log_call_outcome(
    call_outcome: CallOutcome,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    request: Request = None
):
    """
    Log the outcome of a call with a carrier
    
    This endpoint allows the AI to record the complete outcome of a call
    including negotiation details, sentiment, and final result.
    """
    # Validate that required fields are provided
    if not call_outcome.happyrobot_run_id:
        print(call_outcome)
        print(request.body)
        raise HTTPException(status_code=400, detail="happyrobot_run_id is required")
    
    if not call_outcome.call_outcome_classification:
        raise HTTPException(status_code=400, detail="call_outcome_classification is required")
    
    if not call_outcome.carrier_sentiment_classification:
        raise HTTPException(status_code=400, detail="carrier_sentiment_classification is required")
    
    # Check if call log already exists for this happyrobot_run_id
    existing_call = db.query(CallLog).filter(CallLog.happyrobot_run_id == call_outcome.happyrobot_run_id).first()
    if existing_call:
        raise HTTPException(status_code=409, detail="Call log already exists for this happyrobot_run_id")
    
    # Create call log record
    db_call_log = CallLog(
        happyrobot_run_id=call_outcome.happyrobot_run_id,
        mc_number=call_outcome.mc_number,
        searched_load_id=call_outcome.load_id,
        agreed_rate=call_outcome.agreed_rate,
        call_outcome_classification=call_outcome.call_outcome_classification,
        carrier_sentiment_classification=call_outcome.carrier_sentiment_classification,
        fmcsa_verified_eligible=call_outcome.fmcsa_verified_eligible == "ACTIVE",
        initial_carrier_offer=float(call_outcome.initial_carrier_offer) if call_outcome.initial_carrier_offer else None,
        negotiation_rounds=int(call_outcome.negotiation_rounds) if call_outcome.negotiation_rounds else 0,
        raw_extracted_data_json=call_outcome.raw_extracted_data
    )
    
    db.add(db_call_log)
    db.commit()
    db.refresh(db_call_log)
    
    return CallOutcomeResponse(
        status=201,
        message="Call outcome logged successfully",
        call_log_id=db_call_log.id
    )


def validate_api_key_query(api_key: Optional[str] = Query(None, description="API key for authentication")):
    """
    Validate API key from query parameter
    
    Args:
        api_key: API key from query parameter
        
    Returns:
        str: Valid API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key is required. Add '?api_key=your_key' to the URL.",
        )
    
    # Get the expected API key from settings and strip whitespace
    expected_api_key = settings.API_KEY.strip() if settings.API_KEY else None
    
    if not expected_api_key:
        raise HTTPException(
            status_code=500,
            detail="API Key not configured on server",
        )
    
    # Strip whitespace from incoming API key
    clean_api_key = api_key.strip()
    
    if clean_api_key != expected_api_key:
        print(f"Invalid API Key: {clean_api_key} != {expected_api_key}")
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )
    
    return api_key


def safe_currency_format(value):
    """Safely format currency values, handling None and zero values"""
    if value is None:
        return 'N/A'
    try:
        return f"${float(value):.2f}"
    except (TypeError, ValueError):
        return 'N/A'


def safe_date_format(date_value):
    """Safely format datetime values"""
    if date_value is None:
        return 'N/A'
    try:
        return date_value.strftime('%Y-%m-%d %H:%M')
    except (AttributeError, ValueError):
        return 'N/A'


@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(50, description="Maximum number of call logs to display"),
    api_key: str = Depends(validate_api_key_query)
):
    """
    Simple dashboard showing call logs
    
    Returns an HTML dashboard with call log data.
    Requires API key as query parameter: /dashboard?api_key=your_key
    """
    # Get recent call logs
    call_logs = db.query(CallLog).order_by(CallLog.created_at.desc()).limit(limit).all()
    
    # Generate summary statistics with safe calculations
    total_calls = db.query(CallLog).count()
    booked_calls = db.query(CallLog).filter(CallLog.call_outcome_classification.ilike('%book%')).count()
    
    # Calculate average negotiation rounds safely
    avg_negotiation_rounds = db.query(CallLog).filter(CallLog.negotiation_rounds.isnot(None)).with_entities(CallLog.negotiation_rounds).all()
    if avg_negotiation_rounds and len(avg_negotiation_rounds) > 0:
        valid_rounds = [r[0] for r in avg_negotiation_rounds if r[0] is not None]
        avg_rounds = sum(valid_rounds) / len(valid_rounds) if valid_rounds else 0.0
    else:
        avg_rounds = 0.0
    
    # Calculate booking rate safely
    booking_rate = round((booked_calls / total_calls * 100) if total_calls > 0 else 0.0, 1)
    
    # Build HTML response
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Call Logs Dashboard</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }}
            .access-info {{
                background: #e3f2fd;
                border-left: 4px solid #2196f3;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .access-info code {{
                background: #f5f5f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Monaco', 'Menlo', monospace;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 6px;
                border-left: 4px solid #007bff;
            }}
            .stat-value {{
                font-size: 2em;
                font-weight: bold;
                color: #007bff;
            }}
            .stat-label {{
                color: #666;
                margin-top: 5px;
            }}
            .table-container {{
                overflow-x: auto;
                margin-top: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: 600;
                color: #495057;
            }}
            tr:hover {{
                background-color: #f8f9fa;
            }}
            .outcome-booked {{
                background-color: #d4edda;
                color: #155724;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
            }}
            .outcome-rejected {{
                background-color: #f8d7da;
                color: #721c24;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
            }}
            .outcome-other {{
                background-color: #fff3cd;
                color: #856404;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
            }}
            .sentiment-positive {{
                color: #28a745;
                font-weight: 600;
            }}
            .sentiment-negative {{
                color: #dc3545;
                font-weight: 600;
            }}
            .sentiment-neutral {{
                color: #6c757d;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📞 Call Logs Dashboard</h1>
            
            <div class="access-info">
                <strong>🔐 Dashboard Access:</strong> This dashboard requires an API key in the URL.<br>
                <strong>URL Format:</strong> <code>/api/v1/offers/dashboard?api_key=your_key_here</code><br>
                <strong>Additional Options:</strong> Add <code>&limit=100</code> to show more records (default: 50)
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{total_calls}</div>
                    <div class="stat-label">Total Calls</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{booked_calls}</div>
                    <div class="stat-label">Booked Calls</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{booking_rate}%</div>
                    <div class="stat-label">Booking Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{round(avg_rounds, 1)}</div>
                    <div class="stat-label">Avg Negotiation Rounds</div>
                </div>
            </div>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Call Time</th>
                            <th>MC Number</th>
                            <th>Load ID</th>
                            <th>Outcome</th>
                            <th>Sentiment</th>
                            <th>Initial Offer</th>
                            <th>Agreed Rate</th>
                            <th>Negotiation Rounds</th>
                            <th>FMCSA Verified</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for log in call_logs:
        # Format outcome classification
        outcome_class = "outcome-other"
        if log.call_outcome_classification and "book" in log.call_outcome_classification.lower():
            outcome_class = "outcome-booked"
        elif log.call_outcome_classification and ("reject" in log.call_outcome_classification.lower() or "no" in log.call_outcome_classification.lower()):
            outcome_class = "outcome-rejected"
        
        # Format sentiment
        sentiment_class = "sentiment-neutral"
        if log.carrier_sentiment_classification:
            if "positive" in log.carrier_sentiment_classification.lower():
                sentiment_class = "sentiment-positive"
            elif "negative" in log.carrier_sentiment_classification.lower():
                sentiment_class = "sentiment-negative"
        
        html_content += f"""
                        <tr>
                            <td>{safe_date_format(log.called_at)}</td>
                            <td>{log.mc_number or 'N/A'}</td>
                            <td>{log.searched_load_id or 'N/A'}</td>
                            <td><span class="{outcome_class}">{log.call_outcome_classification or 'N/A'}</span></td>
                            <td><span class="{sentiment_class}">{log.carrier_sentiment_classification or 'N/A'}</span></td>
                            <td>{safe_currency_format(log.initial_carrier_offer)}</td>
                            <td>{safe_currency_format(log.agreed_rate)}</td>
                            <td>{log.negotiation_rounds or 0}</td>
                            <td>{'✅' if log.fmcsa_verified_eligible else '❌'}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background-color: #e9ecef; border-radius: 6px; font-size: 12px; color: #666;">
                <strong>Last Updated:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """<br>
                <strong>Records Shown:</strong> """ + str(len(call_logs)) + """ of """ + str(total_calls) + """ total calls<br>
                <strong>Limit:</strong> """ + str(limit) + """ records per page<br>
                <strong>🔄 Refresh:</strong> Reload the page to get the latest data
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


@router.get("/logs", response_model=List[dict])
def get_call_logs(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    limit: Optional[int] = 50,
    offset: Optional[int] = 0
):
    """
    Get call logs as JSON data
    
    This endpoint returns call log data in JSON format for API consumption
    """
    call_logs = db.query(CallLog).order_by(CallLog.created_at.desc()).offset(offset).limit(limit).all()
    
    logs_data = []
    for log in call_logs:
        logs_data.append({
            "id": log.id,
            "happyrobot_run_id": log.happyrobot_run_id,
            "mc_number": log.mc_number,
            "called_at": log.called_at.isoformat() if log.called_at else None,
            "searched_load_id": log.searched_load_id,
            "initial_carrier_offer": log.initial_carrier_offer,
            "negotiation_rounds": log.negotiation_rounds,
            "agreed_rate": log.agreed_rate,
            "call_outcome_classification": log.call_outcome_classification,
            "carrier_sentiment_classification": log.carrier_sentiment_classification,
            "fmcsa_verified_eligible": log.fmcsa_verified_eligible,
            "created_at": log.created_at.isoformat() if log.created_at else None,
            "updated_at": log.updated_at.isoformat() if log.updated_at else None
        })
    
    return logs_data 