#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime
from sqlalchemy import func
from enums import StateEnum
from models import (
  Venue,
  Artist,
  VenueGenre,
  ArtistGenre,
  Show,
  Object
)
from config import app, db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # get a list of all distinct city & state combinations
  cityStateList = db.session.query(Venue.city, Venue.state).distinct()

  #create empty list to hold our venues data
  venuesLists = []

  #loop through each city & state combination
  for item in cityStateList:
    #create an object of an item for "venuesLists" array
    venuesListsItem = Object()

    venuesListsItem.city = item.city
    venuesListsItem.state = StateEnum(int(item.state))
    venuesListsItem.venues = []    

    #get all venues having matching the city & state combination
    venues = db.session.query(Venue.id, Venue.name).filter(Venue.city == item.city, Venue.state == item.state).all()

    #loop through the venues having matching the city & state combination
    for venue in venues:
      #create an object of an item for "venues" array
      venueItem = Object()

      venueItem.id = venue.id
      venueItem.name = venue.name

      #count the number of upcoming shows for the venue
      venueItem.num_upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()

      #append the venue object to the "venues" array
      venuesListsItem.venues.append(venueItem)
    
    #append the venue data object to the "venuesLists" array
    venuesLists.append(venuesListsItem)

  return render_template('pages/venues.html', areas=venuesLists)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  searchTerm = request.form.get('search_term', '')

  results = Object()

  venues = Venue.query.filter(func.lower(Venue.name).contains(func.lower(searchTerm))).all()

  results.count = Venue.query.filter(func.lower(Venue.name).contains(func.lower(searchTerm))).count()
  results.data = []

  for venue in venues:
    venueObject = Object()

    #adding venue id and venue name to the venueObject
    venueObject = venue

    #count the number of upcoming shows for the venue
    venueObject.num_upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()

    results.data.append(venueObject)

  return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)

  venueData = Object()
  venueData = venue

  venueData.past_shows_count = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time < datetime.now()).count()
  venueData.upcoming_shows_count = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
  venueData.past_shows = []
  venueData.upcoming_shows = []
  
  for show in db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time < datetime.now()).all():
    pastShow = Object()

    pastShow.artist_id = show.artist_id
    pastShow.artist_name = Artist.query.get(show.artist_id).name
    pastShow.artist_image_link = Artist.query.get(show.artist_id).image_link
    pastShow.start_time = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

    venueData.past_shows.append(pastShow)

  for show in db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).all():
    upcomingShow = Object()

    upcomingShow.artist_id = show.artist_id
    upcomingShow.artist_name = Artist.query.get(show.artist_id).name
    upcomingShow.artist_image_link = Artist.query.get(show.artist_id).image_link
    upcomingShow.start_time = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

    venueData.upcoming_shows.append(upcomingShow)

  return render_template('pages/show_venue.html', venue=venueData)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  us_phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
  match = re.search(us_phone_num, request.form['phone'])
  if not match:
    flash('Error! phone number must be in format xxx-xxx-xxxx')
    form = VenueForm(obj=venue)  
    return render_template('forms/new_venue.html', form=form, venue=venue)

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_talent = False
    if 'seeking_talent' in request.form:
      if request.form['seeking_talent'] == 'y':
        seeking_talent = True
    seeking_description = request.form['seeking_description']

    genres = []
    for item in request.form.getlist('genres'):
      genres.append(VenueGenre(genre=item))

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link,\
       genres=genres, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
    
    db.session.add(venue)
    db.session.commit()

    db.session.refresh(venue)

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

    db.session.close()

    return redirect(url_for('show_venue', venue_id=venue.id))
  except:
    db.session.rollback()

    print(sys.exc_info())

    # on error db insert, flash failure
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    db.session.close()
    
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)

    for genre in venue.genres:
      db.session.delete(genre)

    venueShows = Show.query.filter(Show.venue_id == venue_id).all()

    db.session.delete(venueShows)
    db.session.delete(venue)

    db.session.commit()

    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()

    print(sys.exc_info())

    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():

  artists = db.session.query(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  searchTerm = request.form.get('search_term', '')

  results = Object()

  artists = Artist.query.filter(func.lower(Artist.name).contains(func.lower(searchTerm))).all()

  results.count = Artist.query.filter(func.lower(Artist.name).contains(func.lower(searchTerm))).count()
  results.data = []

  for artist in artists:
    artistObject = Object()

    #adding artist id and artist name to the artistObject
    artistObject = artist

    #count the number of upcoming shows for the artist
    artistObject.num_upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).count()

    results.data.append(artistObject)

  return render_template('pages/search_artists.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)

  artistData = Object()
  artistData = artist

  artistData.past_shows_count = db.session.query(Show).filter(Show.artist_id == artist.id, Show.start_time < datetime.now()).count()
  artistData.upcoming_shows_count = db.session.query(Show).filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).count()
  artistData.past_shows = []
  artistData.upcoming_shows = []
  
  for show in db.session.query(Show).filter(Show.artist_id == artist.id, Show.start_time < datetime.now()).all():
    pastShow = Object()

    pastShow.venue_id = show.venue_id
    pastShow.venue_name = Venue.query.get(show.venue_id).name
    pastShow.venue_image_link = Venue.query.get(show.venue_id).image_link
    pastShow.start_time = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

    artistData.past_shows.append(pastShow)

  for show in db.session.query(Show).filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).all():
    upcomingShow = Object()

    upcomingShow.artist_id = show.artist_id
    upcomingShow.artist_name = Venue.query.get(show.artist_id).name
    upcomingShow.artist_image_link = Venue.query.get(show.artist_id).image_link
    upcomingShow.start_time = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

    artistData.upcoming_shows.append(upcomingShow)

  return render_template('pages/show_artist.html', artist=artistData)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)

    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.seeking_venue = False
    if 'seeking_venue' in request.form:
      if request.form['seeking_venue'] == 'y':
        artist.seeking_venue = True
    artist.seeking_description = request.form['seeking_description']

    artist.genres = []
    for item in request.form.getlist('genres'):
      artist.genres.append(ArtistGenre(genre=item))

    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

    db.session.close()

    return redirect(url_for('show_artist', artist_id=artist.id))
  except:
    db.session.rollback()

    print(sys.exc_info())

    # on error db insert, flash failure
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')

    db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)

    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent = False
    if 'seeking_talent' in request.form:
      if request.form['seeking_talent'] == 'y':
        venue.seeking_talent = True
    venue.seeking_description = request.form['seeking_description']

    venue.genres = []
    for item in request.form.getlist('genres'):
      venue.genres.append(VenueGenre(genre=item))

    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

    db.session.close()

    return redirect(url_for('show_venue', venue_id=venue.id))
  except:
    db.session.rollback()

    print(sys.exc_info())

    # on error db insert, flash failure
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

    db.session.close()
    
    return render_template('pages/home.html')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  us_phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
  match = re.search(us_phone_num, request.form['phone'])
  if not match:
    flash('Error! phone number must be in format xxx-xxx-xxxx')
    form = ArtistForm(data=request.form)
    return render_template('forms/new_artist.html', form=form)

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_venue = False
    if 'seeking_venue' in request.form:
      if request.form['seeking_venue'] == 'y':
        seeking_venue = True
    seeking_description = request.form['seeking_description']

    genres = []
    for item in request.form.getlist('genres'):
      genres.append(ArtistGenre(genre=item))

    artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, facebook_link=facebook_link,\
      genres=genres, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()

    db.session.refresh(artist)

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

    db.session.close()

    return redirect(url_for('show_artist', artist_id=artist.id))
  except:
    db.session.rollback()

    print(sys.exc_info())

    # on error db insert, flash failure
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    db.session.close()

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = Show.query.all()

  showsData = Object()
  showsData = shows

  for show in showsData:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)

    show.venue_name = venue.name
    show.artist_name = artist.name
    show.artist_image_link = artist.image_link
    show.start_time = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

  return render_template('pages/shows.html', shows=showsData)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
    print(request.form)

    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']

    show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)

    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()

    print(sys.exc_info())

    # on error db insert, flash failure
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/shows/search', methods=['POST'])
def search_shows():

  searchTerm = request.form.get('search_term', '')

  shows = Show.query.all()

  showsData = Object()
  showsData = []

  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)

    showData = Object()
    showData = show

    showData.venue_name = venue.name
    showData.artist_name = artist.name
    showData.artist_image_link = artist.image_link
    showData.start_time = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

    if (searchTerm.lower() in artist.name.lower()) or (searchTerm.lower() in venue.name.lower()):
      showsData.append(showData)

  results = Object()
  results.data = showsData
  results.count = len(showsData)

  return render_template('pages/search_shows.html', results=results, search_term=request.form.get('search_term', ''))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
  return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''