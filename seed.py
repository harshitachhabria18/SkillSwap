from app import create_app, db
from app.models import Skills

app = create_app()

with app.app_context():
    skills = [
        'Python', 'JavaScript', 'Java', 'C++', 'Flask',
        'React', 'Machine Learning', 'Data Science',
        'Graphic Design', 'Digital Marketing', 'Communication',
        'Public Speaking', 'Video Editing', 'Photography',
        'Java', 'Node.js', 'SQL', 'MongoDB'
        # add all your skills here
    ]
    
    for skill_name in skills:
        existing = Skills.query.filter_by(name=skill_name).first()
        if not existing:
            skill = Skills(name=skill_name)
            db.session.add(skill)
    
    db.session.commit()
    print("Skills seeded successfully!")