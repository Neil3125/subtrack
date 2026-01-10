"""Export routes for generating reports."""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import get_db
from app.models import Subscription, Customer, Category
from io import BytesIO
import csv

router = APIRouter()


@router.get("/export/subscriptions/excel")
async def export_subscriptions_excel(db: Session = Depends(get_db)):
    """Export subscriptions to Excel format."""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Subscriptions"
        
        # Headers
        headers = ["ID", "Vendor", "Plan", "Cost", "Currency", "Billing Cycle", "Status", 
                   "Customer", "Category", "Next Renewal", "Notes"]
        ws.append(headers)
        
        # Style headers
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
        
        # Get data
        subscriptions = db.query(Subscription).all()
        
        for sub in subscriptions:
            ws.append([
                sub.id,
                sub.vendor_name,
                sub.plan_name or "",
                float(sub.cost),
                sub.currency,
                sub.billing_cycle.value,
                sub.status.value,
                sub.customer.name if sub.customer else "",
                sub.category.name if sub.category else "",
                sub.next_renewal_date.isoformat() if sub.next_renewal_date else "",
                sub.notes or ""
            ])
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=subscriptions_{date.today().isoformat()}.xlsx"}
        )
    except ImportError:
        # Fallback to CSV if openpyxl not available
        return await export_subscriptions_csv(db)


@router.get("/export/subscriptions/csv")
async def export_subscriptions_csv(db: Session = Depends(get_db)):
    """Export subscriptions to CSV format."""
    output = BytesIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(["ID", "Vendor", "Plan", "Cost", "Currency", "Billing Cycle", "Status", 
                     "Customer", "Category", "Next Renewal", "Notes"])
    
    # Data
    subscriptions = db.query(Subscription).all()
    for sub in subscriptions:
        writer.writerow([
            sub.id,
            sub.vendor_name,
            sub.plan_name or "",
            sub.cost,
            sub.currency,
            sub.billing_cycle.value,
            sub.status.value,
            sub.customer.name if sub.customer else "",
            sub.category.name if sub.category else "",
            sub.next_renewal_date.isoformat() if sub.next_renewal_date else "",
            sub.notes or ""
        ])
    
    output.seek(0)
    return Response(
        content=output.getvalue().decode('utf-8'),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=subscriptions_{date.today().isoformat()}.csv"}
    )


@router.get("/export/analytics/excel")
async def export_analytics_excel(db: Session = Depends(get_db)):
    """Export analytics report to Excel."""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.chart import BarChart, Reference
        
        wb = openpyxl.Workbook()
        
        # Summary sheet
        ws_summary = wb.active
        ws_summary.title = "Summary"
        
        # Get data
        active_subs = db.query(Subscription).filter(Subscription.status == "active").all()
        all_subs = db.query(Subscription).all()
        
        total_cost = sum(s.cost for s in active_subs)
        
        # Summary data
        ws_summary.append(["SubTrack Analytics Report"])
        ws_summary.append([f"Generated: {date.today().isoformat()}"])
        ws_summary.append([])
        ws_summary.append(["Metric", "Value"])
        ws_summary.append(["Total Active Subscriptions", len(active_subs)])
        ws_summary.append(["Total Monthly Cost", f"${total_cost:.2f}"])
        ws_summary.append(["Average Cost per Subscription", f"${total_cost/len(active_subs):.2f}" if active_subs else "$0.00"])
        ws_summary.append(["Total Subscriptions (All Status)", len(all_subs)])
        
        # Style summary
        ws_summary['A1'].font = Font(size=16, bold=True)
        ws_summary['A1'].fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        ws_summary['A1'].font = Font(size=16, bold=True, color="FFFFFF")
        
        for row in ws_summary['A4:B8']:
            for cell in row:
                if cell.column == 1:
                    cell.font = Font(bold=True)
        
        # By Category sheet
        ws_category = wb.create_sheet("By Category")
        ws_category.append(["Category", "Count", "Total Cost"])
        
        categories = db.query(Category).all()
        for cat in categories:
            cat_subs = [s for s in active_subs if s.category_id == cat.id]
            cat_cost = sum(s.cost for s in cat_subs)
            ws_category.append([cat.name, len(cat_subs), cat_cost])
        
        # Style headers
        for cell in ws_category[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
        
        # By Vendor sheet
        ws_vendor = wb.create_sheet("By Vendor")
        ws_vendor.append(["Vendor", "Count", "Total Cost"])
        
        from collections import defaultdict
        vendor_stats = defaultdict(lambda: {"count": 0, "total": 0})
        for sub in active_subs:
            vendor_stats[sub.vendor_name]["count"] += 1
            vendor_stats[sub.vendor_name]["total"] += sub.cost
        
        for vendor, stats in sorted(vendor_stats.items(), key=lambda x: x[1]["total"], reverse=True):
            ws_vendor.append([vendor, stats["count"], stats["total"]])
        
        # Style headers
        for cell in ws_vendor[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
        
        # Save
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=analytics_report_{date.today().isoformat()}.xlsx"}
        )
    except ImportError:
        # Fallback to CSV
        output = BytesIO()
        writer = csv.writer(output)
        
        writer.writerow(["SubTrack Analytics Report"])
        writer.writerow([f"Generated: {date.today().isoformat()}"])
        writer.writerow([])
        
        active_subs = db.query(Subscription).filter(Subscription.status == "active").all()
        total_cost = sum(s.cost for s in active_subs)
        
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Active Subscriptions", len(active_subs)])
        writer.writerow(["Total Monthly Cost", f"${total_cost:.2f}"])
        
        output.seek(0)
        return Response(
            content=output.getvalue().decode('utf-8'),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analytics_report_{date.today().isoformat()}.csv"}
        )
