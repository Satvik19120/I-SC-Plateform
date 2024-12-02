from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, sponsor, influencer

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(50), nullable=False)  # public or private
    goals = db.Column(db.String(150), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sponsor = db.relationship('User', backref=db.backref('campaigns', lazy=True))

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Pending, Accepted, Rejected
    campaign = db.relationship('Campaign', backref=db.backref('ad_requests', lazy=True))
    influencer = db.relationship('User', backref=db.backref('ad_requests', lazy=True))





'''# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, sponsor, influencer
    compaign=db.relationship("Campaign",cascade="all,delete", backref="user")
    adrequest=db.relationship("AdRequest",cascade="all,delete", backref="user")
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(50), nullable=False)  # public or private
    goals = db.Column(db.String(150), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #sponsor = db.relationship('User', backref=db.backref('campaigns', lazy=True))
    adrequest=db.relationship("AdRequest",cascade="all,delete", backref="campaign")
class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Pending, Accepted, Rejected
    #campaign = db.relationship('Campaign', backref=db.backref('ad_requests', lazy=True))
    #influencer = db.relationship('User', backref=db.backref('ad_requests', lazy=True))
    #--koi kam nhi upr h isi table me influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
'''








# Authentication Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'sponsor':
                return redirect(url_for('sponsor_dashboard'))
            elif user.role == 'influencer':
                return redirect(url_for('influencer_dashboard'))
        else:
            flash('Login failed. Check your credentials and try again.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    total_users = User.query.count()
    total_campaigns = Campaign.query.count()
    total_ad_requests = AdRequest.query.count()
    flagged_users = []  # Example: fetch flagged users
    flagged_campaigns = []  # Example: fetch flagged campaigns
    return render_template('admin_dashboard.html', total_users=total_users, total_campaigns=total_campaigns, total_ad_requests=total_ad_requests, flagged_users=flagged_users, flagged_campaigns=flagged_campaigns)

@app.route('/flag_user/<int:user_id>')
@login_required
def flag_user(user_id):
    # Example: Implement flagging logic
    flash('User flagged successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/flag_campaign/<int:campaign_id>')
@login_required
def flag_campaign(campaign_id):
    # Example: Implement flagging logic
    flash('Campaign flagged successfully.')
    return redirect(url_for('admin_dashboard'))

# Sponsor Routes
@app.route('/sponsor_dashboard')
@login_required
def sponsor_dashboard():
    if current_user.role != 'sponsor':
        return redirect(url_for('index'))
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    influencers=User.query.filter_by(role='influencer')
    ad_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == current_user.id).all()
    return render_template('sponsor_dashboard.html', campaigns=campaigns, ad_requests=ad_requests,influencers=influencers)

@app.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if current_user.role != 'sponsor':
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        budget = float(request.form['budget'])
        visibility = request.form['visibility']
        goals = request.form['goals']
        new_campaign = Campaign(name=name, description=description, start_date=start_date, end_date=end_date, budget=budget, visibility=visibility, goals=goals, sponsor_id=current_user.id)
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!')
        return redirect(url_for('sponsor_dashboard'))
    return render_template('create_campaign.html')

@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    if current_user.role != 'sponsor':
        return redirect(url_for('index'))
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != current_user.id:
        return redirect(url_for('sponsor_dashboard'))
    if request.method == 'POST':
        campaign.name = request.form['name']
        campaign.description = request.form['description']
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        campaign.budget = float(request.form['budget'])
        campaign.visibility = request.form['visibility']
        campaign.goals = request.form['goals']
        db.session.commit()
        flash('Campaign updated successfully!')
        return redirect(url_for('sponsor_dashboard'))
    return render_template('edit_campaign.html', campaign=campaign)

@app.route('/delete_campaign/<int:campaign_id>')
@login_required
def delete_campaign(campaign_id):
    if current_user.role != 'sponsor':
        return redirect(url_for('index'))
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id == current_user.id:
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully!')
    else:
        flash('You are not authorized to delete this campaign.')
    return redirect(url_for('sponsor_dashboard'))



@app.route('/create_ad_request', methods=['POST'])
@login_required
def create_ad_request():
    if current_user.role != 'sponsor':
        return redirect(url_for('index'))
    visibility=request.form['visibility']
    campaign_id = request.form['campaign_id']
    #influencer_id = request.form['influencer_id']
    requirements = request.form['requirements']
    payment_amount = float(request.form['payment_amount'])
    influencers = request.form.getlist('influencers') if visibility == 'private' else []
    if visibility=='private':
        for influencer in influencers:
            new_ad_request = AdRequest(
                campaign_id=campaign_id,
                influencer_id=influencer.id,
                requirements=requirements,
                payment_amount=payment_amount,
                status='Pending'
            )
            db.session.add(new_ad_request)
            db.session.commit()
            
            flash('Ad request sent successfully!', 'success')
            return redirect(url_for('sponsor_dashboard'))
    
    influencers = User.query.filter_by(role='influencer').all()
    for influencer in influencers:
            new_ad_request = AdRequest(
                campaign_id=campaign_id,
                influencer_id=influencer.id,
                requirements=requirements,
                payment_amount=payment_amount,
                status='Pending'
            )
            db.session.add(new_ad_request)
            db.session.commit()
            
            flash('Ad request sent successfully!', 'success')
            return redirect(url_for('sponsor_dashboard'))



# influencer Routes
@app.route('/influencer_dashboard')
@login_required
def influencer_dashboard():
    if current_user.role != 'influencer':
        return redirect(url_for('index'))
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    return render_template('influencer_dashboard.html', ad_requests=ad_requests)
    return redirect(url_for('index'))
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    ad_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == current_user.id).all()
    return render_template('sponsor_dashboard.html', campaigns=campaigns, ad_requests=ad_requests)





@app.route('/view_ad_requests')
@login_required
def view_ad_requests():
    if current_user.role == 'sponsor':
        ad_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == current_user.id).all()
    elif current_user.role == 'influencer':
        ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    else:
        return redirect(url_for('index'))
    return render_template('view_ad_requests.html', ad_requests=ad_requests)

@app.route('/ad_request_detail/<int:ad_request_id>')
@login_required
def ad_request_detail(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    return render_template('ad_request_detail.html', ad_request=ad_request)

@app.route('/accept_ad_request/<int:ad_request_id>')
@login_required
def accept_ad_request(ad_request_id):
    if current_user.role != 'influencer':
        return redirect(url_for('index'))
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.influencer_id == current_user.id and ad_request.status == 'Pending':
        ad_request.status = 'Accepted'
        db.session.commit()
        flash('Ad request accepted.')
    else:
        flash('You are not authorized to accept this ad request.')
    return redirect(url_for('view_ad_requests'))

@app.route('/reject_ad_request/<int:ad_request_id>')
@login_required
def reject_ad_request(ad_request_id):
    if current_user.role != 'influencer':
        return redirect(url_for('index'))
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.influencer_id == current_user.id and ad_request.status == 'Pending':
        ad_request.status = 'Rejected'
        db.session.commit()
        flash('Ad request rejected.')
    else:
        flash('You are not authorized to reject this ad request.')
    return redirect(url_for('view_ad_requests'))

@app.route('/negotiate_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
def negotiate_ad_request(ad_request_id):
    if current_user.role != 'influencer':
        return redirect(url_for('index'))
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.influencer_id != current_user.id or ad_request.status != 'Pending':
        return redirect(url_for('view_ad_requests'))
    if request.method == 'POST':
        ad_request.payment_amount = float(request.form['payment_amount'])
        ad_request.requirements = request.form['requirements']
        ad_request.status = 'Pending'  # or another status if needed
        db.session.commit()
        flash('Ad request updated successfully.')
        return redirect(url_for('view_ad_requests'))
    return render_template('negotiate_ad_request.html', ad_request=ad_request)

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if current_user.role != 'influencer':
        return redirect(url_for('index'))
    if request.method == 'POST':
        current_user.username = request.form['name']
        # Update other profile fields as needed
        db.session.commit()
        flash('Profile updated successfully.')
    return render_template('update_profile.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
