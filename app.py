from flask import Flask , render_template , url_for ,redirect,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin , login_user,LoginManager,login_required,logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField ,SubmitField ,FloatField
from wtforms.validators import InputRequired , Length , ValidationError
from flask_bcrypt import Bcrypt



# app initailize
app = Flask(__name__)


# for secure password
bcrypt = Bcrypt(app)

# database connection
# sqlite database for stroing the movies and user information
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)


# flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#  user model username , password and is_admin for admin and normal user is_asmin-0 => normal user is_admin -1 => admin
class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),nullable=False,unique=True)
    password = db.Column(db.String(80),nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


#  movie model to store name director name genre , imdb_score etc in sqlite database
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    director = db.Column(db.String(200))
    popularity = db.Column(db.Float)
    imdb_score = db.Column(db.Float)
    genre = db.Column(db.String(255))



# data population
# import json
# with open('imdb.json','r') as f
# data = json.load(f)
#for entry in data:
# new_movie = Movie(name = entry['name],popularity = entry['99popularity],genre = entry['genre],imdb_score = entry['imdb_score],director = rntry['director'])
# db.session.add(new_movie)
#db.session.commit()



#  Registration form
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


#  Login form
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

#  for adding new movie only admin have the access
class AddMovieForm(FlaskForm):
    name = StringField(validators=[InputRequired()],render_kw={"placeholder": "MovieName"})
    director = StringField(validators=[InputRequired()],render_kw={"placeholder": "Director"})
    genre = StringField(validators=[InputRequired()],render_kw={"placeholder": "Genre"})
    popularity = FloatField(validators=[InputRequired()],render_kw={"placeholder": "popularity"})
    imdb_score = FloatField(validators=[InputRequired()],render_kw={"placeholder": "imdb_score"})
    submit = SubmitField('AddMovie')
    
# updating form for the updating the existing movie
class UpdateFrom(FlaskForm):
    name = StringField(validators=[InputRequired()],render_kw={"placeholder": "MovieName"})
    director = StringField(validators=[InputRequired()],render_kw={"placeholder": "Director"})
    genre = StringField(validators=[InputRequired()],render_kw={"placeholder": "Genre"})
    popularity = FloatField(validators=[InputRequired()],render_kw={"placeholder": "popularity"})
    imdb_score = FloatField(validators=[InputRequired()],render_kw={"placeholder": "imdb_score"})
    submit = SubmitField('UpdateMovie')

# for searching the movie user can search by name , director and genre also
class SearchForm(FlaskForm):
    name = StringField(render_kw={"placeholder": "MovieName"})
    director = StringField(render_kw={"placeholder": "Director"})
    genre = StringField(render_kw={"placeholder": "Genre"})
    submit = SubmitField('SearchMovies')
    

# home route for the normal user where user can see the listing of movies and can search the movie 
@app.route('/')
@login_required
def home():
    form = SearchForm()
    movies = Movie.query.all() # fecthing all movies from movie table in sqlite database for displaying them on home page
    return render_template('home.html',movies=movies,form=form) # rendering to the home page after succssfull completing the api call


# admin user home route where admin can add a new movie , delete a existing movie and can update the existing movie and also have the funcnality of normal user
@app.route('/admin',methods=['GET'])
@login_required
def admin(): 
    if current_user.is_admin: # checking for the admin because only admin can access this route
        form = SearchForm()
        movies = Movie.query.all() # fetching all the movies 
        return render_template('Admin.html',movies=movies,form=form) # rendring to the admin page and sending movies and flask form for searching movies


# delete route for the admin where admin can delete a movie form database using their unique ID
@app.route('/admin/delete/<int:id>')
@login_required
def delete(id):
    if current_user.is_admin: # checking for the admin
        movie = Movie.query.get_or_404(id) # fetching the movie form database using movie id 
        try:
            db.session.delete(movie) # deleting the movie from database
            db.session.commit()
            return redirect(url_for('admin')) # after successfully deleting the movie redirecting to admin page
        except:
            return 'There is problem deleting the movie' # error message if any error accours


# update route for the admin where admin can update the movie on sqlite database by the movie ID   
@app.route('/admin/update/<int:id>',methods=['GET','POST'])
@login_required
def update(id):
    if current_user.is_admin: # checking for the admin
        movie = Movie.query.get_or_404(id) # geting the movie by movie ID
        form = UpdateFrom(name = movie.name , director=movie.director,genre=movie.genre,popularity=movie.popularity,imdb_score=movie.imdb_score)
        if request.method == 'POST': # taking information by update form to update the movie
            movie.name = form.name.data
            movie.director = form.director.data
            movie.genre = form.genre.data
            movie.popularity = form.popularity.data
            movie.imdb_score = form.imdb_score.data

            try:
                db.session.commit()
                return redirect(url_for('admin')) # on successfully updation going back admin page
            except:
                return 'There is some error in updating the movie' # error message in case any error
        else:
            return render_template('update.html',movie=movie,form=form) # going to the update page
    else :
        return "Only admin can access!!!" # error message




#  search funcnality for both normal user and admin
# they can search  based on various criteria lke name of the movie , genre of the movie , director of the movie and we can implement more in this sections
@app.route('/movies/search',methods=['GET','POST'])
@login_required
def search_movies():
    form = SearchForm() # search form
    if request.method == 'POST': # geting data form search form
        movie_name = form.name.data
        movie_genre = form.genre.data
        movie_director = form.director.data

        query = Movie.query # geting movie by query
        if movie_name:
            query = query.filter(Movie.name.ilike(f'%{movie_name}')) # filtering by name

        if movie_genre:
            query = query.filter_by(genre=movie_genre) # filter_by genre
        if movie_director:
            query = query.filter_by(director=movie_director) # filter_by director
        
        movies = query.all() # executing all querys and fetching reault in movies search fresult
        return render_template('search_result.html',movies=movies) # going to search result page
     

# login route for the users
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm() # login form
    if form.validate_on_submit(): # on validating form 
        user = User.query.filter_by(username=form.username.data).first() # geting the username form database
        if user: # if user exists
            if bcrypt.check_password_hash(user.password ,form.password.data): # comparing passwords 
                login_user(user) # seting the user
                if current_user.is_admin: # checking the role of user for identifying that it is normal user or admin
                    return redirect(url_for('admin')) # if admin then go to the admin page
                else:
                    return redirect(url_for('home')) # else go the the home page
    return render_template('login.html',form=form) # if password or username not found the stay at login page



# in this route admin can add new movie 
@app.route('/admin/add_movie',methods=['GET','POST'])
@login_required
def addMovie():
    form = AddMovieForm()
    if current_user.is_admin & form.validate_on_submit(): # on admin have access to add the movies 
        movie = Movie(name = form.name.data,director=form.director.data,genre=form.genre.data,popularity=form.popularity.data,imdb_score=form.imdb_score.data) # getting data form flask form 
        db.session.add(movie) # adding new movie to the database
        db.session.commit()
        return redirect(url_for('admin')) # on success go to admin page
    return render_template('AddMovie.html',form=form) ## if not stay there



# logout route for both normal user and admin
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user() # logout user
    return redirect(url_for('login'))



# signup/register route for user
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data) # geting hashed password
        new_user = User(username = form.username.data,password=hashed_password) # getting datat for user from form
        db.session.add(new_user) #adding new user to the database
        db.session.commit()
        return redirect(url_for('login')) # on suucess full go to login page
    return render_template('register.html',form=form) # else stay here



# running the flask app
if __name__ == '__main__':
    
    app.run(debug=True)

