from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from app.forms import EditProfileForm
from flask_login import current_user, login_required
from app import db
from app.models import Skills, UserSkills
from werkzeug.utils import secure_filename
import os
import uuid

# a small app(blueprint) for managing user backend 
user_bp = Blueprint('user', __name__, url_prefix='/user', template_folder='templates')

# route for user_profile page (Screen 3)
@user_bp.route('/user_profile', methods=["GET","POST"])
@login_required
def home():
    # here form is the object of EditProfileForm class from forms.py
    form = EditProfileForm()

    # UPLOAD_FOLDER points to the server-side folder (like static/images/) where the uploaded photo will be saved after the user uploads it.
    # for example-
    # /home/harshita/projects/skillswap/static/images - current_app.root_path + static + images
    UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static', 'images')
    # Ensures that the UPLOAD_FOLDER directory actually exists. If it doesn’t exist, it creates it
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # get all the rows of Skills table in all_skills variable
    all_skills = Skills.query.all()
    # converts all_skills [
#     Skill(id=1, name="Python"),
#     Skill(id=2, name="Web Development"),
#     Skill(id=3, name="Graphic Design")
#     ] in this format into list of tuples that is [(1,"Python"),(2,"Web Development"),(3,"Graphic Design")]
    form.skills_offered.choices = [(skill.id, skill.name) for skill in all_skills]
    form.skills_wanted.choices = [(skill.id, skill.name) for skill in all_skills]

    if request.method == "POST" and 'remove_photo' in request.form:
        if current_user.profile_photo:
            old_path = os.path.join(UPLOAD_FOLDER, current_user.profile_photo)
            if os.path.exists(old_path):
                os.remove(old_path)
            current_user.profile_photo = None
            db.session.commit()
            flash("Profile photo removed.", "info")
        return redirect(url_for('user.home'))


    if request.method == "POST" and form.validate_on_submit():
        # the current_user is the instance or full row of the User table and stores the values of properties like name, location, entered by the user in the form in the User table after db.session.commit()
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.availability = form.availability.data
        current_user.session_duration = form.session_duration.data
        current_user.profile_visibility = form.profile_type.data

        # handle photo upload
        # get the photo which is uploaded inside the variable file
        file = form.photo.data
        # checks if the file exists and filename is not empty
        if file and file.filename != '':
            # for securing the file or converting it into safe version
            # here uuid is used for giving unique ids to photos having same file names
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            # .path.join combines the upload_folder and the filename (here, static/images/myphoto.png)
            # /home/harshita/projects/skillswap/static/images/abc123.jpg - full path example
            photo_path = os.path.join(UPLOAD_FOLDER, filename)
            # saves the file in the photo_path location
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(photo_path)

            # remove old photo/image if it exists from the static/images folder
            if current_user.profile_photo:
                # variable old path now contains full path of old profile photo (example: static/images/myphoto.png(current photo address))
                old_path = os.path.join(UPLOAD_FOLDER, current_user.profile_photo)
                # if old photo exists, remove it from the static folder
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # store the new photo filename in User table using current_user
            current_user.profile_photo = filename

        # this variable contains the list of ids stored in the hiddeninput field through JavaScript where selected fiels ids are stored
        # for example - ("1,2,4")
        skills_offered_str = request.form.get('skills_offered_list', '')
        skills_offered_ids = set()

        skills_wanted_str = request.form.get('skills_wanted_list', '')
        # {'2', '5'} - duplicates are removed if any from the list 
        skills_wanted_ids = set()

        # for each id in ['1','2','4'] (loop through each field)
        for skill_id in skills_offered_str.split(','):
            if skill_id.strip():
                # {2,4} - ids are added in set like this
                skills_offered_ids.add(int(skill_id.strip()))

        for skill_id in skills_wanted_str.split(','):
            if skill_id.strip():
                skills_wanted_ids.add(int(skill_id.strip()))

        # rows of UserSkills table of current user id
        existing_skills = UserSkills.query.filter_by(user_id=current_user.id).all()

        # Loops through all UserSkills rows of the current user (existing_skills).

        # Filters only those where skill_type == 'offered'.

        # Collects the skills_id of each — i.e., the ID from the Skills table.

        # Stores them in a Python set (to avoid duplicates automatically).

        # returns set of offered or wanted ids from the database like {1,2,3}
        existing_offered_ids = {skill.skills_id for skill in existing_skills if skill.skill_type == 'offered'}
        existing_wanted_ids = {skill.skills_id for skill in existing_skills if skill.skill_type == 'wanted'}
        
        # for the first time existing_offered_ids = set() -> empty set
        # and skills_offered_ids = {2,5} -> for example

        # set() - {2,5} = set() -> so nothing is removed
        # {2,5} - set() = {2,5} -> so these skills are now added in database

        # now after the data is stored in the database:
        # existing_offered_ids = {2,5} -> fetched from the database
        # skills_offered_ids = {3,5} -> user makes changes in UI and so hidden inputs is also updated

        # {2,5} - {3,5} = {2} -> skill_id = 2 record should be removed from database
        # {3,5} - {2,5} = {3} -> skill_id = 3 record should be added to database

        skills_offered_to_remove = existing_offered_ids - skills_offered_ids
        skills_offered_to_add = skills_offered_ids - existing_offered_ids

        skills_wanted_to_remove = existing_wanted_ids - skills_wanted_ids
        skills_wanted_to_add = skills_wanted_ids - existing_wanted_ids

        # filter the record having current user's id, type = "offered" and skills_id = 2 (id to be removed)/ the set of ids to be removed and delete it
        UserSkills.query.filter(
            UserSkills.user_id == current_user.id,
            UserSkills.skill_type == 'offered',
            UserSkills.skills_id.in_(skills_offered_to_remove)
        ).delete(synchronize_session=False)

        UserSkills.query.filter(
            UserSkills.user_id == current_user.id,
            UserSkills.skill_type == 'wanted',
            UserSkills.skills_id.in_(skills_wanted_to_remove)
        ).delete(synchronize_session=False)


        # store the user_id, skill_id and type offered in database
        for skill_id in skills_offered_to_add:
            db.session.add(UserSkills(user_id=current_user.id, skills_id=skill_id, skill_type="offered"))

        # for each id in ['3']
        # store the user_id, skill_id and type wanted in database
        for skill_id in skills_wanted_to_add:
            db.session.add(UserSkills(user_id=current_user.id, skills_id=skill_id, skill_type="wanted"))


        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for('user.home'))

    # if the same user logs in again and get request is generated, the data is fetched from the database
    elif request.method == "GET":
        form.name.data = current_user.name
        form.location.data = current_user.location
        form.availability.data = current_user.availability
        form.session_duration.data = current_user.session_duration
        form.profile_type.data = current_user.profile_visibility

    # stores the list of offered skills like this
    #     [
    # <Skills id=1 name="Python">,
    # <Skills id=2 name="Web Development">
    # ] -> is stored in selected_skills_offered

    # Looping through UserSkills of the user

    # Filtering only those where skill_type == 'offered'

    # Collecting the actual Skills object (skill.skill) for each

    selected_skills_offered = [skill.skill for skill in current_user.user_skills if skill.skill_type == 'offered']
    selected_skills_wanted = [skill.skill for skill in current_user.user_skills if skill.skill_type == 'wanted']

    return render_template('user/profile.html', form=form,
                            selected_skills_offered=selected_skills_offered,
                            selected_skills_wanted=selected_skills_wanted) 
