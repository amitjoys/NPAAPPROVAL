from tasks.celery_app import celery_app
from weasyprint import HTML, CSS
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    def generate_nfa_html(nfa_data: dict, approval_history: list) -> str:
        """Generate HTML for NFA PDF"""
        s1 = nfa_data.get("section1_data", {})
        s2 = nfa_data.get("section2_data", {})
        
        # Generate approval signatures HTML
        section1_approvals = [a for a in approval_history if a["section"] == 1]
        section2_approvals = [a for a in approval_history if a["section"] == 2]
        
        section1_sigs = ""
        for approval in section1_approvals:
            section1_sigs += f"""
            <div class="signature-box">
                <p><strong>Name:</strong> {approval['approver_name']}</p>
                <p><strong>Designation:</strong> {approval['approver_designation']}</p>
                <p><strong>Date:</strong> {approval.get('action_timestamp', '')[:10] if approval.get('action_timestamp') else 'Pending'}</p>
            </div>
            """
        
        section2_sigs = """
        for approval in section2_approvals:
            section2_sigs += f"""
            <div class="signature-box">
                <p><strong>Name:</strong> {approval['approver_name']}</p>
                <p><strong>Designation:</strong> {approval['approver_designation']}</p>
                <p><strong>Date:</strong> {approval.get('action_timestamp', '')[:10] if approval.get('action_timestamp') else 'Pending'}</p>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 10pt; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px; }}
                .header h1 {{ margin: 0; font-size: 14pt; }}
                .header p {{ margin: 5px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
                table, th, td {{ border: 1px solid #000; }}
                th, td {{ padding: 6px; text-align: left; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .section-title {{ background-color: #e0e0e0; font-weight: bold; padding: 8px; margin-top: 15px; }}
                .signature-container {{ display: flex; justify-content: space-between; margin-top: 20px; }}
                .signature-box {{ border: 1px solid #000; padding: 10px; width: 30%; min-height: 80px; }}
                .footer {{ margin-top: 30px; padding-top: 10px; border-top: 2px solid #000; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>HCIL - Honda Cars India Limited</h1>
                <h2>NFA FOR REQUEST FOR WORK/ EXPENSE/ INCOME AND VENDOR SELECTION</h2>
                <p><strong>Annexure-4</strong></p>
                {f'<p><strong>NFA Number: {nfa_data.get("nfa_number", "DRAFT")}</strong></p>' if nfa_data.get("nfa_number") else ''}
            </div>
            
            <table>
                <tr>
                    <th>OPERATION/DIVISION (USER)</th>
                    <td>{s1.get('function_division', '')}</td>
                    <th>LOCATION</th>
                    <td>{s1.get('location', '')}</td>
                </tr>
                <tr>
                    <th>FROM (ASSOC. NAME)</th>
                    <td>{s1.get('requestor_name', '')}</td>
                    <th>COST CODE</th>
                    <td>{s1.get('cost_code', '')}</td>
                </tr>
                <tr>
                    <th>DEPARTMENT</th>
                    <td>{s1.get('department', '')}</td>
                    <th>DATE</th>
                    <td>{nfa_data.get('created_at', '')[:10]}</td>
                </tr>
            </table>
            
            <table>
                <tr>
                    <th colspan="4">SUBJECT/ITEM</th>
                </tr>
                <tr>
                    <td colspan="4">{s1.get('subject_item', '')}</td>
                </tr>
            </table>
            
            <table>
                <tr>
                    <th colspan="4">BACKGROUND & PURPOSE</th>
                </tr>
                <tr>
                    <td colspan="4">{s1.get('background_purpose', '')}</td>
                </tr>
            </table>
            
            <div class="section-title">SECTION - 1 (Work Approval to be filled by User)</div>
            
            <table>
                <tr>
                    <th>PROPOSAL</th>
                    <td colspan="3">{s1.get('proposal_description', '')}</td>
                </tr>
                <tr>
                    <th>Proposed Work Schedule</th>
                    <td colspan="3">{s1.get('proposed_work_schedule', '')}</td>
                </tr>
            </table>
            
            <div class="section-title">FINANCIAL DETAILS</div>
            
            <table>
                <tr>
                    <th>Budget Status</th>
                    <td>{s1.get('budget_status', '')}</td>
                    <th>Budget Available with User</th>
                    <td>{'Yes' if s1.get('budget_available_with_user') else 'No'}</td>
                </tr>
                <tr>
                    <th>Amount of Approval</th>
                    <td>{s1.get('currency', 'INR')} {s1.get('amount_of_approval', 0):,.2f}</td>
                    <th>Tax Status</th>
                    <td>{s1.get('tax_status', '')}</td>
                </tr>
                <tr>
                    <th>Advance Payment Required</th>
                    <td>{'Yes' if s1.get('advance_payment_required') else 'No'}</td>
                    <th>Advance Amount</th>
                    <td>{s1.get('advance_amount', 0) if s1.get('advance_payment_required') else 'N/A'}</td>
                </tr>
            </table>
            
            <div class="section-title">SECTION - 2 (Vendor Selection & Final Cost Approval)</div>
            
            <table>
                <tr>
                    <th>Activity Approved</th>
                    <td>{'Yes' if s2.get('vendor_selection') else 'No'}</td>
                    <th>No. of Vendors Evaluated</th>
                    <td>{s2.get('num_vendors_evaluated', 'N/A')}</td>
                </tr>
                <tr>
                    <th>Name of Vendor Proposed</th>
                    <td colspan="3">{s2.get('vendor_name_proposed', '')}</td>
                </tr>
                <tr>
                    <th>Amount of Approval</th>
                    <td>{s1.get('currency', 'INR')} {s2.get('amount_of_approval', 0):,.2f}</td>
                    <th>Tax Status</th>
                    <td>{s2.get('tax_status', '')}</td>
                </tr>
                <tr>
                    <th colspan="4">Comments</th>
                </tr>
                <tr>
                    <td colspan="4">{s2.get('comments', '')}</td>
                </tr>
            </table>
            
            <div class="section-title">Section 1 Approvals</div>
            <div class="signature-container">
                {section1_sigs}
            </div>
            
            <div class="section-title">Section 2 Approvals</div>
            <div class="signature-container">
                {section2_sigs}
            </div>
            
            <div class="footer">
                <p><strong>Generated on:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>NFA Automation System v1.0</strong></p>
            </div>
        </body>
        </html>
        """
        
        return html

@celery_app.task(name="tasks.generate_nfa_pdf")
def generate_nfa_pdf(nfa_id: str):
    """Generate PDF for NFA"""
    try:
        # Import here to avoid circular imports
        import asyncio
        from motor.motor_asyncio import AsyncIOMotorClient
        from core.config import settings
        
        async def async_generate():
            # Connect to database
            client = AsyncIOMotorClient(settings.MONGO_URL)
            db = client[settings.DB_NAME]
            
            # Get NFA data
            nfa = await db.nfa_requests.find_one({"id": nfa_id}, {"_id": 0})
            if not nfa:
                logger.error(f"NFA not found: {nfa_id}")
                return False
            
            # Get approval history
            approvals = await db.approval_workflows.find(
                {"nfa_id": nfa_id},
                {"_id": 0}
            ).sort([("section", 1), ("sequence", 1)]).to_list(100)
            
            # Generate HTML
            html_content = PDFService.generate_nfa_html(nfa, approvals)
            
            # Create PDF directory if not exists
            pdf_dir = "/app/backend/generated_pdfs"
            os.makedirs(pdf_dir, exist_ok=True)
            
            # Generate PDF
            pdf_path = f"{pdf_dir}/NFA_{nfa_id}.pdf"
            HTML(string=html_content).write_pdf(pdf_path)
            
            logger.info(f"PDF generated: {pdf_path}")
            
            # Finalize NFA
            from services.nfa_service import NFAService
            await NFAService.finalize_nfa(nfa_id, pdf_path)
            
            # Send notification
            from tasks.email_tasks import send_final_nfa_notification
            requestor = await db.users.find_one({"id": nfa["requestor_id"]}, {"_id": 0})
            if requestor:
                send_final_nfa_notification.delay(
                    nfa_id,
                    requestor["email"],
                    nfa.get("nfa_number", "DRAFT"),
                    pdf_path
                )
            
            client.close()
            return True
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_generate())
        loop.close()
        
        return result
    except Exception as e:
        logger.error(f"Error generating PDF for NFA {nfa_id}: {e}")
        return False
