import json
import os
import sys
import argparse
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description="Generate GRC Compliance Report PDF and stats JSON.")
    parser.add_argument("--checklist", required=True, help="Path to checklist JSON")
    parser.add_argument("--device", required=True, help="Device name")
    parser.add_argument("--host", required=True, help="Host name")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Report date (default: today)")
    parser.add_argument("--output_dir", default="reports", help="Directory to save reports")
    return parser.parse_args()

def summarize_checklist(checklist):
    total = len(checklist)
    compliant = sum(1 for x in checklist if x["status"].lower() == "compliant")
    non_compliant = sum(1 for x in checklist if x["status"].lower() == "non-compliant")
    skipped = sum(1 for x in checklist if x["status"].lower() == "skipped")
    compliance_pct = (compliant / total) * 100 if total > 0 else 0
    return {
        "total": total,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "skipped": skipped,
        "compliance_pct": round(compliance_pct, 1)
    }

def create_pie_chart(stats, output_path):
    labels = ['Compliant', 'Non-Compliant', 'Skipped']
    sizes = [stats['compliant'], stats['non_compliant'], stats['skipped']]
    colors = ['#66bb6a', '#ef5350', '#ffa726']
    explode = [0.05 if s == max(sizes) and s > 0 else 0 for s in sizes]
    plt.figure(figsize=(4, 4))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.0f%%', startangle=140)
    plt.title('Compliance Status')
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'GRC Compliance Report', ln=True, align='C')
        self.ln(2)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, title, ln=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 7, body)
        self.ln(1)

def generate_grc_pdf(checklist, stats, device, host, date, pie_img_path, output_pdf_path):
    pdf = PDF()
    pdf.add_page()

    # Header info
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"Device Name: {device}", ln=True)
    pdf.cell(0, 8, f"Host Name: {host}", ln=True)
    pdf.cell(0, 8, f"Date: {date}", ln=True)
    pdf.ln(4)

    # Executive Summary
    pdf.chapter_title("Executive Summary")
    summary = (
        f"Total Controls Evaluated: {stats['total']}\n"
        f"Compliant: {stats['compliant']}\n"
        f"Non-Compliant: {stats['non_compliant']}\n"
        f"Skipped: {stats['skipped']}\n"
        f"Compliance Percentage: {stats['compliance_pct']}%"
    )
    pdf.chapter_body(summary)
    pdf.ln(2)

    # Pie Chart
    if os.path.exists(pie_img_path):
        pdf.chapter_title("Compliance Status Chart")
        pdf.image(pie_img_path, x=pdf.get_x()+30, w=80)
        pdf.ln(8)

    # Detailed Checklist
    pdf.chapter_title("Detailed Checklist")
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(25, 8, "Control ID", border=1)
    pdf.cell(85, 8, "Title", border=1)
    pdf.cell(30, 8, "Status", border=1)
    pdf.cell(0, 8, "Notes", border=1, ln=True)
    pdf.set_font('Arial', '', 10)
    for item in checklist:
        pdf.cell(25, 8, str(item["id"]), border=1)
        pdf.cell(85, 8, str(item["title"])[:50] + ('...' if len(item["title"]) > 50 else ''), border=1)
        status = str(item["status"]).capitalize()
        # Color status
        if status == "Compliant":
            pdf.set_text_color(102, 187, 106)
        elif status == "Non-compliant":
            pdf.set_text_color(239, 83, 80)
        elif status == "Skipped":
            pdf.set_text_color(255, 167, 38)
        pdf.cell(30, 8, status, border=1)
        pdf.set_text_color(0, 0, 0)
        note = str(item.get("note", ""))[:30] + ('...' if len(item.get("note", "")) > 30 else '')
        pdf.cell(0, 8, note, border=1, ln=True)
    pdf.ln(8)

    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, "This report is generated automatically. For queries, contact your GRC team.", ln=True, align='C')

    pdf.output(output_pdf_path)

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # Load checklist
    with open(args.checklist, "r", encoding="utf-8") as f:
        checklist = json.load(f)

    # Calculate stats
    stats = summarize_checklist(checklist)

    # Pie chart
    pie_img_path = os.path.join(args.output_dir, "compliance_pie.png")
    create_pie_chart(stats, pie_img_path)

    # PDF output
    pdf_name = f"{args.device}_{args.host}_GRC_REPORT_{args.date}.pdf"
    pdf_path = os.path.join(args.output_dir, pdf_name)
    generate_grc_pdf(checklist, stats, args.device, args.host, args.date, pie_img_path, pdf_path)

    # Save stats JSON
    stats_json = {
        "device": args.device,
        "host": args.host,
        "date": args.date,
        **stats
    }
    stats_path = os.path.join(args.output_dir, f"{args.device}_{args.host}_GRC_STATS_{args.date}.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats_json, f, indent=2)

    print(f"[+] GRC PDF Report saved to: {pdf_path}")
    print(f"[+] Compliance stats JSON saved to: {stats_path}")

if __name__ == "__main__":
    main()