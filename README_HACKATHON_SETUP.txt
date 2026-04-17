# AI Student Early Warning Dashboard - Hackathon Package

Files included:
- `student_dashboard_webhook_workflow.json` -> import this into n8n
- `app.py` -> run this Streamlit dashboard
- `requirements.txt` -> install Python packages

## Step 1: Start Streamlit
Open CMD in this folder and run:
pip install -r requirements.txt
python -m streamlit run app.py

If `streamlit` command is not recognized, always use:
python -m streamlit run app.py

## Step 2: Import n8n workflow
1. Open n8n
2. Import `student_dashboard_webhook_workflow.json`
3. Open the `Webhook` node
4. Copy the Production URL
5. Activate the workflow

## Step 3: Connect Streamlit to n8n
1. Paste the n8n Production Webhook URL in the Streamlit sidebar
2. Upload CSV or click `Use Demo Data`
3. Click `Run n8n Workflow`

## Required CSV columns
Student_ID, Student_Name, Class, Section, Physics_Marks, Chemistry_Marks, Math_Marks,
Attendance_Percentage, Homework_Completion_Percentage, Parent_Email, Teacher_Email, Phone_Number

## n8n response fields
- success
- summary
- teacher_alert_list
- all_students_processed
- email_subject
- email_body

## Notes
- This version uses dummy alert generation only, so it runs without Gmail/Twilio setup.
- You can later add Gmail, Google Sheets, or WhatsApp nodes after `Build Dummy Alert`.
