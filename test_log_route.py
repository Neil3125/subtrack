import sys, os, traceback
sys.path.append(os.getcwd())
from app.routers.log_check_routes import LogGenerateRequest, generate_log, parse_human_time

def test():
    try:
        # 1. Test basic Service Check JSON schema validation
        payload = {"check_type": "service", "mode": "automatic", "hours": 0, "minutes": 30}
        req = LogGenerateRequest(**payload)
        print("Schema validated successfully:", req)
        
        # 2. Test manual mode schema
        payload_manual = {
            "check_type": "custom",
            "mode": "manual",
            "start_time": "10:30 AM",
            "end_time": "11:00 AM",
            "date_str": "02/27/2026",
            "message": "Custom message"
        }
        req_manual = LogGenerateRequest(**payload_manual)
        print("Manual schema valid:", req_manual)
        
        # 3. Test parse_human_time with Flatpickr am/pm output format
        print("parse_human_time '10:30 AM':", parse_human_time("10:30 AM"))
        print("parse_human_time '02:00 PM':", parse_human_time("02:00 PM"))
        
        print("All tests passed.")
    except Exception as e:
        print("Error encountered:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
