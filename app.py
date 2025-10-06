from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config.from_object(config['development'])

db = SQLAlchemy(app)

# Database Model for Resources
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    campus = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    contact_info = db.Column(db.String(200))

    def __repr__(self):
        return f'<Resource {self.name}>'

# Helper function to get college logo filename
def get_college_logo(college_name):
    """Map college names to their logo filenames"""
    logo_map = {
        'Baruch College': 'baruch.jpeg',
        'Borough of Manhattan Community College': 'bmcc.png',
        'Bronx Community College': 'bronx.png',
        'Brooklyn College': 'brooklyn.jpg',
        'City College of New York': 'ccny.jpeg',
        'Hunter College': 'hunter.png',
        'John Jay College': 'jjay.jpeg',
        'Lehman College': 'lehman.png',
        'Queens College': 'queens.jpeg',
        'York College': 'york.jpeg'
    }
    return logo_map.get(college_name, 'CRH-logo.png')  # Default to CRH logo if not found

# Make the helper function available in templates
app.jinja_env.globals.update(get_college_logo=get_college_logo)

# Routes
@app.route('/')
def index():
    """Home page - displays all colleges"""
    # Get unique colleges from the database
    colleges = db.session.query(Resource.campus).distinct().order_by(Resource.campus).all()
    colleges = [college[0] for college in colleges]
    return render_template('index.html', colleges=colleges)

@app.route('/college/<college_name>')
def college_detail(college_name):
    """Display resources for a specific college"""
    resources = Resource.query.filter_by(campus=college_name).all()
    if not resources:
        return render_template('404.html', college=college_name), 404
    return render_template('college_detail.html', college=college_name, resources=resources)

@app.route('/search')
def search():
    """Search page - allows filtering resources"""
    query = request.args.get('q', '')
    campus = request.args.get('campus', '')
    category = request.args.get('category', '')

    resources_query = Resource.query

    if query:
        resources_query = resources_query.filter(
            db.or_(
                Resource.name.contains(query),
                Resource.description.contains(query)
            )
        )

    if campus:
        resources_query = resources_query.filter_by(campus=campus)

    if category:
        resources_query = resources_query.filter_by(category=category)

    resources = resources_query.all()
    return render_template('search.html', resources=resources, query=query, campus=campus, category=category)

@app.route('/resource/<int:resource_id>')
def resource_detail(resource_id):
    """Display detailed information about a specific resource"""
    resource = Resource.query.get_or_404(resource_id)
    return render_template('resource_detail.html', resource=resource)

@app.route('/api/resources')
def api_resources():
    """API endpoint to get resources as JSON"""
    resources = Resource.query.all()
    resources_list = []
    for resource in resources:
        resources_list.append({
            'id': resource.id,
            'name': resource.name,
            'description': resource.description,
            'campus': resource.campus,
            'category': resource.category,
            'url': resource.url,
            'contact_info': resource.contact_info
        })
    return jsonify(resources_list)

@app.route('/analytics')
def analytics():
    """Basic analytics page using Pandas and Matplotlib"""
    resources = Resource.query.all()
    df = pd.DataFrame([{
        'campus': r.campus,
        'category': r.category
    } for r in resources])

    if not df.empty:
        # Create a simple bar chart of resources by campus
        campus_counts = df['campus'].value_counts()
        plt.figure(figsize=(10, 6))
        campus_counts.plot(kind='bar')
        plt.title('Resources by Campus')
        plt.xlabel('Campus')
        plt.ylabel('Number of Resources')
        plt.tight_layout()

        # Save the plot
        static_dir = os.path.join(app.root_path, 'static', 'images')
        os.makedirs(static_dir, exist_ok=True)
        plot_path = os.path.join(static_dir, 'campus_distribution.png')
        plt.savefig(plot_path)
        plt.close()

        return render_template('analytics.html', plot_url='/static/images/campus_distribution.png')
    else:
        return render_template('analytics.html', plot_url=None)

import click
import pandas as pd

@app.cli.command("import_resources")
def import_resources():
    """Import resources from resources.csv into the database."""
    csv_path = 'resources.csv'
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        click.echo(f"CSV file not found at path: {csv_path}")
        return
    except Exception as e:
        click.echo(f"Error reading CSV file: {e}")
        return

    # Map CSV columns to Resource model fields
    # CSV columns: College,Resource,Type,Link,Description,Email
    # Resource model fields: campus, name, category, url, description, contact_info

    # Clean dataframe: drop empty rows
    df = df.dropna(subset=['College', 'Resource'])

    count = 0
    for _, row in df.iterrows():
        # Check if resource already exists by name and campus
        existing_resource = Resource.query.filter_by(name=row['Resource'], campus=row['College']).first()
        if existing_resource:
            # Update existing resource
            existing_resource.description = row.get('Description', '') or ''
            existing_resource.category = row.get('Type', '') or ''
            existing_resource.url = row.get('Link', '') or ''
            existing_resource.contact_info = row.get('Email', '') or ''
        else:
            # Create new resource
            new_resource = Resource(
                name=row['Resource'],
                description=row.get('Description', '') or '',
                campus=row['College'],
                category=row.get('Type', '') or '',
                url=row.get('Link', '') or '',
                contact_info=row.get('Email', '') or ''
            )
            db.session.add(new_resource)
        count += 1

    db.session.commit()
    click.echo(f"Imported or updated {count} resources from {csv_path}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
