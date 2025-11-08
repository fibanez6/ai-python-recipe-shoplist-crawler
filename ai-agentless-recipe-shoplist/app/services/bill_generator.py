"""Bill generator service for creating formatted shopping receipts."""

import json
import os
import uuid
from datetime import datetime
from typing import Optional

# PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..models import Bill, OptimizationResult, Recipe


class BillGenerator:
    """Generates shopping bills in various formats."""
    
    def __init__(self):
        self.company_name = "AI Recipe Shoplist"
        self.company_address = "Smart Shopping Solutions"
        self.tax_rate = 0.10  # 10% GST in Australia
        self.currency = "AUD"
        self.bills_directory = "generated_bills"
        
        # Create bills directory if it doesn't exist
        os.makedirs(self.bills_directory, exist_ok=True)
    
    async def generate_bill(self, recipe: Recipe, optimization_result: OptimizationResult,
                          format: str = "pdf") -> Bill:
        """Generate a shopping bill from recipe and optimization results."""
        print(f"[BillGenerator] Generating {format.upper()} bill for '{recipe.title}'")
        
        # Create bill object
        bill_id = str(uuid.uuid4())[:8]
        generated_at = datetime.now().isoformat()
        
        # Calculate totals
        subtotal = optimization_result.total_cost
        tax_amount = subtotal * self.tax_rate
        total = subtotal + tax_amount
        
        # Get list of stores
        stores = list(set(
            item.selected_product.store 
            for item in optimization_result.items 
            if item.selected_product
        ))
        
        bill = Bill(
            id=bill_id,
            recipe_title=recipe.title,
            generated_at=generated_at,
            items=optimization_result.items,
            subtotal=subtotal,
            tax_rate=self.tax_rate,
            tax_amount=tax_amount,
            total=total,
            stores=stores
        )
        
        # Generate the actual bill file
        if format.lower() == "pdf":
            await self._generate_pdf_bill(bill, recipe)
        elif format.lower() == "html":
            await self._generate_html_bill(bill, recipe)
        elif format.lower() == "json":
            await self._generate_json_bill(bill, recipe)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return bill
    
    async def _generate_pdf_bill(self, bill: Bill, recipe: Recipe) -> str:
        """Generate PDF bill using ReportLab."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab not available. Install with: pip install reportlab")
        
        filename = f"{self.bills_directory}/bill_{bill.id}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_LEFT
        )
        
        # Title
        story.append(Paragraph(f"{self.company_name}", title_style))
        story.append(Paragraph("Shopping List & Cost Estimate", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Bill info
        bill_info = f"""
        <b>Bill ID:</b> {bill.id}<br/>
        <b>Recipe:</b> {bill.recipe_title}<br/>
        <b>Generated:</b> {datetime.fromisoformat(bill.generated_at).strftime('%Y-%m-%d %H:%M')}<br/>
        <b>Stores to Visit:</b> {', '.join(bill.stores)}
        """
        story.append(Paragraph(bill_info, header_style))
        story.append(Spacer(1, 20))
        
        # Items table
        table_data = [['Item', 'Quantity', 'Store', 'Price', 'Total']]
        
        for item in bill.items:
            if item.selected_product:
                quantity_str = f"{item.quantity_needed:.1f}"
                if item.ingredient.unit:
                    quantity_str += f" {item.ingredient.unit}"
                
                table_data.append([
                    item.ingredient.name,
                    quantity_str,
                    item.selected_product.store,
                    f"${item.selected_product.price:.2f}",
                    f"${item.estimated_cost:.2f}" if item.estimated_cost else "$0.00"
                ])
            else:
                table_data.append([
                    item.ingredient.name,
                    f"{item.quantity_needed:.1f}",
                    "Not found",
                    "-",
                    "$0.00"
                ])
        
        # Create table
        table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),  # Right align prices
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Totals
        totals_data = [
            ['Subtotal:', f"${bill.subtotal:.2f}"],
            [f'Tax ({bill.tax_rate*100:.0f}%):', f"${bill.tax_amount:.2f}"],
            ['', ''],  # Spacer row
            ['Total:', f"${bill.total:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[4*inch, 1*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 30))
        
        # Store breakdown
        if bill.stores:
            story.append(Paragraph("Store Breakdown:", styles['Heading3']))
            for store_name, store_cost in bill.stores_breakdown.items():
                if store_name != "travel":
                    story.append(Paragraph(f"• {store_name}: ${store_cost:.2f}", styles['Normal']))
            
            if "travel" in bill.stores_breakdown:
                story.append(Paragraph(f"• Travel costs: ${bill.stores_breakdown['travel']:.2f}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Footer
        footer_text = f"""
        <i>Generated by {self.company_name}<br/>
        This is an estimate based on current prices.<br/>
        Actual prices may vary.</i>
        """
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        print(f"[BillGenerator] PDF bill saved to: {filename}")
        
        return filename
    
    async def _generate_html_bill(self, bill: Bill, recipe: Recipe) -> str:
        """Generate HTML bill."""
        filename = f"{self.bills_directory}/bill_{bill.id}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Shopping Bill - {bill.recipe_title}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .bill-container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .company-name {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #007bff;
                    margin: 0;
                }}
                .bill-info {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 30px;
                }}
                .bill-info h3 {{
                    margin-top: 0;
                    color: #333;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 30px;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #007bff;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                .price {{
                    text-align: right;
                    font-weight: bold;
                }}
                .totals {{
                    border: 2px solid #007bff;
                    padding: 20px;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                }}
                .total-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 5px 0;
                }}
                .final-total {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #007bff;
                    border-top: 2px solid #007bff;
                    padding-top: 10px;
                    margin-top: 10px;
                }}
                .stores-section {{
                    margin-top: 30px;
                    padding: 20px;
                    background-color: #e7f3ff;
                    border-radius: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 14px;
                }}
                .not-found {{
                    color: #dc3545;
                    font-style: italic;
                }}
                @media print {{
                    body {{ background-color: white; }}
                    .bill-container {{ box-shadow: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="bill-container">
                <div class="header">
                    <h1 class="company-name">{self.company_name}</h1>
                    <h2>Shopping List & Cost Estimate</h2>
                </div>
                
                <div class="bill-info">
                    <h3>Bill Information</h3>
                    <p><strong>Bill ID:</strong> {bill.id}</p>
                    <p><strong>Recipe:</strong> {bill.recipe_title}</p>
                    <p><strong>Generated:</strong> {datetime.fromisoformat(bill.generated_at).strftime('%Y-%m-%d %H:%M')}</p>
                    <p><strong>Stores to Visit:</strong> {', '.join(bill.stores) if bill.stores else 'None'}</p>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Quantity</th>
                            <th>Store</th>
                            <th>Unit Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add items
        for item in bill.items:
            quantity_str = f"{item.quantity_needed:.1f}"
            if item.ingredient.unit:
                quantity_str += f" {item.ingredient.unit}"
            
            if item.selected_product:
                html_content += f"""
                        <tr>
                            <td>{item.ingredient.name}</td>
                            <td>{quantity_str}</td>
                            <td>{item.selected_product.store}</td>
                            <td class="price">${item.selected_product.price:.2f}</td>
                            <td class="price">${item.estimated_cost:.2f if item.estimated_cost else 0:.2f}</td>
                        </tr>
                """
            else:
                html_content += f"""
                        <tr>
                            <td>{item.ingredient.name}</td>
                            <td>{quantity_str}</td>
                            <td class="not-found">Not found</td>
                            <td class="price">-</td>
                            <td class="price">$0.00</td>
                        </tr>
                """
        
        # Add totals and footer
        html_content += f"""
                    </tbody>
                </table>
                
                <div class="totals">
                    <div class="total-row">
                        <span>Subtotal:</span>
                        <span>${bill.subtotal:.2f}</span>
                    </div>
                    <div class="total-row">
                        <span>Tax ({bill.tax_rate*100:.0f}%):</span>
                        <span>${bill.tax_amount:.2f}</span>
                    </div>
                    <div class="total-row final-total">
                        <span>Total:</span>
                        <span>${bill.total:.2f}</span>
                    </div>
                </div>
        """
        
        if hasattr(bill, 'stores_breakdown') and bill.stores_breakdown:
            html_content += f"""
                <div class="stores-section">
                    <h3>Store Breakdown</h3>
                    <ul>
            """
            for store_name, store_cost in bill.stores_breakdown.items():
                if store_name == "travel":
                    html_content += f"<li>Travel costs: ${store_cost:.2f}</li>"
                else:
                    html_content += f"<li>{store_name}: ${store_cost:.2f}</li>"
            html_content += "</ul></div>"
        
        html_content += f"""
                <div class="footer">
                    <p><em>Generated by {self.company_name}</em></p>
                    <p>This is an estimate based on current prices. Actual prices may vary.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[BillGenerator] HTML bill saved to: {filename}")
        return filename
    
    async def _generate_json_bill(self, bill: Bill, recipe: Recipe) -> str:
        """Generate JSON bill for API consumption."""
        filename = f"{self.bills_directory}/bill_{bill.id}.json"
        
        # Convert bill to dict for JSON serialization
        bill_data = {
            "bill_id": bill.id,
            "recipe_title": bill.recipe_title,
            "generated_at": bill.generated_at,
            "items": [],
            "subtotal": bill.subtotal,
            "tax_rate": bill.tax_rate,
            "tax_amount": bill.tax_amount,
            "total": bill.total,
            "stores": bill.stores,
            "currency": self.currency
        }
        
        for item in bill.items:
            item_data = {
                "ingredient": {
                    "name": item.ingredient.name,
                    "quantity": item.quantity_needed,
                    "unit": item.ingredient.unit,
                    "original_text": item.ingredient.original_text
                },
                "estimated_cost": item.estimated_cost
            }
            
            if item.selected_product:
                item_data["selected_product"] = {
                    "title": item.selected_product.title,
                    "price": item.selected_product.price,
                    "store": item.selected_product.store,
                    "brand": item.selected_product.brand,
                    "size": item.selected_product.size,
                    "url": item.selected_product.url
                }
            else:
                item_data["selected_product"] = None
            
            bill_data["items"].append(item_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(bill_data, f, indent=2, ensure_ascii=False)
        
        print(f"[BillGenerator] JSON bill saved to: {filename}")
        return filename
    
    def get_bill_path(self, bill_id: str, format: str = "pdf") -> Optional[str]:
        """Get the file path for a generated bill."""
        filename = f"{self.bills_directory}/bill_{bill_id}.{format.lower()}"
        if os.path.exists(filename):
            return filename
        return None
    
    async def generate_receipt_summary(self, bill: Bill) -> str:
        """Generate a short receipt summary for display."""
        summary = f"""
        🧾 Shopping Receipt Summary
        
        Recipe: {bill.recipe_title}
        Bill ID: {bill.id}
        
        Items: {len([item for item in bill.items if item.selected_product])}
        Stores: {len(bill.stores)}
        
        Subtotal: ${bill.subtotal:.2f}
        Tax: ${bill.tax_amount:.2f}
        Total: ${bill.total:.2f}
        
        Generated: {datetime.fromisoformat(bill.generated_at).strftime('%Y-%m-%d %H:%M')}
        """
        return summary.strip()


# Global bill generator instance
bill_generator = BillGenerator()