"""
This module generates an automated weekly welfare report.
It summarizes key findings from trend analysis and anomaly detection,
and generates a report in a human-readable format (Markdown).
"""

import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os


def generate_weekly_report(trend_analysis_results, anomaly_detection_results, output_path='reports/weekly_report.pdf'):
    """
    Generates a weekly welfare report summarizing trend analysis and anomaly detection results.

    Args:
        trend_analysis_results (dict): A dictionary containing trend analysis results.
                                        Example: {
                                            'food_prices': {'trend': 'increasing', 'rate': 0.05},
                                            'health_indicators': {'trend': 'decreasing', 'rate': -0.02}
                                        }
        anomaly_detection_results (dict): A dictionary containing anomaly detection results.
                                          Example: {
                                              'region_A': {'metric': 'malnutrition_rate', 'value': 0.15, 'expected': 0.08},
                                              'region_B': {'metric': 'disease_outbreak', 'value': 100, 'expected': 20}
                                          }
        output_path (str): The path to save the generated report (default: 'reports/weekly_report.pdf').
    """

    try:
        # Create the 'reports' directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Weekly Welfare Report", styles['h1']))
        story.append(Spacer(1, 0.2*inch))

        # Trend Analysis Summary
        story.append(Paragraph("Trend Analysis Summary", styles['h2']))
        if trend_analysis_results:
            for metric, data in trend_analysis_results.items():
                trend = data.get('trend', 'N/A')
                rate = data.get('rate', 'N/A')
                story.append(Paragraph(f"- {metric}: Trend is {trend}, Rate is {rate}", styles['Normal']))
        else:
            story.append(Paragraph("No trend analysis results available.", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        # Anomaly Detection Summary
        story.append(Paragraph("Anomaly Detection Summary", styles['h2']))
        if anomaly_detection_results:
            for region, data in anomaly_detection_results.items():
                metric = data.get('metric', 'N/A')
                value = data.get('value', 'N/A')
                expected = data.get('expected', 'N/A')
                story.append(Paragraph(f"- {region}: {metric} is {value}, Expected: {expected}", styles['Normal']))
        else:
            story.append(Paragraph("No anomaly detection results available.", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        # Example plot (replace with actual plots if available)
        # Generate a dummy plot
        plt.figure(figsize=(6, 4))
        plt.plot([1, 2, 3, 4], [5, 6, 7, 8])
        plt.title('Example Plot')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.savefig('temp_plot.png')  # Save the plot to a temporary file

        try:
            img = Image('temp_plot.png', width=4*inch, height=3*inch)
            story.append(img)
        except Exception as e:
            story.append(Paragraph(f"Error including plot: {e}", styles['Normal']))

        # Build the PDF document
        doc.build(story)

        # Clean up temporary plot file
        try:
            os.remove('temp_plot.png')
        except OSError as e:
            print(f"Error deleting temporary plot file: {e}")

        print(f"Weekly report generated successfully at {output_path}")

    except Exception as e:
        print(f"Error generating weekly report: {e}")


if __name__ == '__main__':
    # Example usage:
    trend_data = {
        'food_prices': {'trend': 'increasing', 'rate': 0.05},
        'health_indicators': {'trend': 'decreasing', 'rate': -0.02}
    }
    anomaly_data = {
        'region_A': {'metric': 'malnutrition_rate', 'value': 0.15, 'expected': 0.08},
        'region_B': {'metric': 'disease_outbreak', 'value': 100, 'expected': 20}
    }
    generate_weekly_report(trend_data, anomaly_data)
