"""
HTML Email Templates for safety notifications.

Provides styled HTML templates for violation alerts and daily reports.
All CSS is inline for email client compatibility.
"""


def violation_alert_template(worker_name: str, worker_id: str,
                              missing_ppe: list, timestamp: str,
                              violation_count: int) -> str:
    """Generate HTML for a PPE violation alert email.

    Args:
        worker_name: Worker's full name
        worker_id: Worker ID
        missing_ppe: List of missing PPE item names
        timestamp: Formatted timestamp string
        violation_count: Today's violation count for this worker

    Returns:
        HTML string
    """
    missing_items_html = ''.join(
        f'<li style="padding:4px 0;font-size:16px;">&#x26A0; {item.upper()}</li>'
        for item in missing_ppe
    )

    required_ppe_html = '''
        <li>Safety Helmet</li>
        <li>Safety Gloves</li>
        <li>Safety Vest</li>
        <li>Safety Shoes</li>
        <li>Protection Glasses</li>
    '''

    return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;background:#f4f4f4;">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;">

  <!-- HEADER -->
  <tr>
    <td style="background:#dc2626;padding:24px;text-align:center;">
      <h1 style="color:#ffffff;margin:0;font-size:24px;">&#x1F6A8; Safety Alert</h1>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td style="background:#ffffff;padding:32px;">
      <p style="font-size:16px;color:#333;">Dear <strong>{worker_name}</strong>,</p>
      <p style="font-size:14px;color:#555;">
        This is an automated safety notification from the Workplace Safety Monitoring System.
        A PPE compliance violation has been detected.
      </p>

      <!-- ALERT BOX -->
      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#fef3c7;border-left:4px solid #f59e0b;padding:16px;margin:20px 0;">
        <tr><td>
          <p style="margin:0 0 8px 0;font-weight:bold;color:#92400e;font-size:16px;">
            Missing PPE Items:
          </p>
          <ul style="margin:0;padding-left:20px;color:#92400e;">
            {missing_items_html}
          </ul>
        </td></tr>
      </table>

      <!-- VIOLATION DETAILS -->
      <table width="100%" cellpadding="8" cellspacing="0"
             style="background:#f3f4f6;border-radius:4px;margin:20px 0;">
        <tr>
          <td style="color:#6b7280;font-size:13px;border-bottom:1px solid #e5e7eb;">
            Date &amp; Time</td>
          <td style="color:#111;font-size:13px;border-bottom:1px solid #e5e7eb;">
            {timestamp}</td>
        </tr>
        <tr>
          <td style="color:#6b7280;font-size:13px;border-bottom:1px solid #e5e7eb;">
            Worker ID</td>
          <td style="color:#111;font-size:13px;border-bottom:1px solid #e5e7eb;">
            {worker_id}</td>
        </tr>
        <tr>
          <td style="color:#6b7280;font-size:13px;">Violation Count (Today)</td>
          <td style="color:#111;font-size:13px;">{violation_count}</td>
        </tr>
      </table>

      <!-- VIOLATION IMAGE -->
      <p style="text-align:center;margin:20px 0;">
        <img src="cid:violation_image" alt="Violation Screenshot"
             style="max-width:100%;border:1px solid #e5e7eb;border-radius:4px;" />
      </p>

      <!-- ACTION REQUIRED -->
      <p style="font-size:14px;color:#333;font-weight:bold;">Action Required:</p>
      <p style="font-size:14px;color:#555;">Please ensure all PPE is worn at all times:</p>
      <ul style="font-size:14px;color:#555;line-height:1.8;">
        {required_ppe_html}
      </ul>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#6b7280;padding:16px;text-align:center;">
      <p style="color:#e5e7eb;margin:0;font-size:12px;">
        Workplace Safety Monitoring System &mdash; Automated Alert
      </p>
    </td>
  </tr>

</table>
</body>
</html>'''


def daily_report_template(report_date: str, violations: list,
                           total_violations: int) -> str:
    """Generate HTML for a daily safety summary report.

    Args:
        report_date: Report date string
        violations: List of dicts with keys: worker_name, worker_id, timestamp, missing_ppe, count
        total_violations: Total violation count for the day

    Returns:
        HTML string
    """
    rows_html = ''
    for v in violations:
        missing = ', '.join(v.get('missing_ppe', []))
        rows_html += f'''
        <tr>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;font-size:13px;">{v.get('worker_name','')}</td>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;font-size:13px;">{v.get('worker_id','')}</td>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;font-size:13px;">{v.get('timestamp','')}</td>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;font-size:13px;">{missing}</td>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;font-size:13px;text-align:center;">{v.get('count',0)}</td>
        </tr>'''

    if not rows_html:
        rows_html = '''
        <tr>
          <td colspan="5" style="padding:16px;text-align:center;color:#6b7280;font-size:13px;">
            No violations recorded today.
          </td>
        </tr>'''

    return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;background:#f4f4f4;">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:700px;margin:0 auto;">

  <!-- HEADER -->
  <tr>
    <td style="background:#1e40af;padding:24px;text-align:center;">
      <h1 style="color:#fff;margin:0;font-size:22px;">Daily Safety Report</h1>
      <p style="color:#bfdbfe;margin:8px 0 0;font-size:14px;">Report Date: {report_date}</p>
    </td>
  </tr>

  <!-- SUMMARY -->
  <tr>
    <td style="background:#ffffff;padding:24px;">
      <p style="font-size:18px;color:#111;margin:0 0 16px;">
        Total Violations: <strong style="color:#dc2626;">{total_violations}</strong>
      </p>

      <!-- VIOLATIONS TABLE -->
      <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e7eb;border-radius:4px;">
        <thead>
          <tr style="background:#f9fafb;">
            <th style="padding:10px;text-align:left;font-size:13px;color:#374151;border-bottom:2px solid #e5e7eb;">Worker</th>
            <th style="padding:10px;text-align:left;font-size:13px;color:#374151;border-bottom:2px solid #e5e7eb;">ID</th>
            <th style="padding:10px;text-align:left;font-size:13px;color:#374151;border-bottom:2px solid #e5e7eb;">Time</th>
            <th style="padding:10px;text-align:left;font-size:13px;color:#374151;border-bottom:2px solid #e5e7eb;">Missing PPE</th>
            <th style="padding:10px;text-align:center;font-size:13px;color:#374151;border-bottom:2px solid #e5e7eb;">Count</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#6b7280;padding:16px;text-align:center;">
      <p style="color:#e5e7eb;margin:0;font-size:12px;">
        Automatically generated by Workplace Safety Monitoring System
      </p>
    </td>
  </tr>

</table>
</body>
</html>'''
