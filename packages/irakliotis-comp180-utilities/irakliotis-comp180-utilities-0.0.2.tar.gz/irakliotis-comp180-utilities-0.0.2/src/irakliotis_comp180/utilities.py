# Miscellaneous utilities for COMP 180 (Computing & Data)

def decode_metar_wind(wind_string):
  """A simple function to decode a METAR wind string to three integers.
  The string is in the format (spaces added for clarity; not present actually;
  hash marks indicate numerals 0 through 9):

     ### ## [G##] KT
     --- --  ---  --
      |   |    |   |
      |   |    |   +---> KT stands for knots -- a unit of speed
      |   |    |         common in flying and sailing; 1 knot is
      |   |    |         1 nautical mile per hour; a nautical mile
      |   |    |         equivalent to 1.15078 statutory miles.
      |   |    |
      |   |    +-------> When the letter G is present, it is followed by two
      |   |              numbers indicating wing gust speeds.
      |   |
      |   +------------> This group of two numbers is always present, to
      |                  indicate wind speed, up to 99 knots. No wind is
      |                  shown as 00.
      |
      +----------------> This group of three numbers shows wind direction 
                         (where is the wind blowing from). It ranges from
                         000 to 350 and is always reported in increments of 10.

  Strings can be in one of these two forms: #####KT or #####G##KT and so the
  can be parsed as follows:

  0123456789   <-- index position in string
  #####KT      <-- string form when no gusting
  #####G##KT   <-- string form for gusting

  Substring [0:3] ... the direction of the wind
  Substring [3:5] ... the speed of the wind
  Substring [6:8] ... the gust speed (if string longer than 7 characters).
     
  The function returns three integer values. The first two correspond to wind 
  direction and wind speed. If the input string includes gusting information,
  the third value corresponds to wind gusting speed.
  """
  # Wind direction is always in the first three characters of the string.
  wind_direction = int(wind_string[0:3])  
  # Wind speed is the next two characters
  wind_speed = int(wind_string[3:5])
  # Assume there is no gusting
  wind_gust = None
  if len(wind_string) > 7:
    # Wind string longer than 7 characters, it contains gust info, get it.
    wind_gust = int(wind_string[6:8])
  # return data to the caller
  return wind_direction, wind_speed, wind_gust


def translate_metar(wind_string):
  """Function to convert METAR wind string to plain language.
  The function recognizes cardinal and intercardinal directions, in 45 degree
  segments. It begins from the intercardinal segment with the highest direction,
  and proceeds down from there, in an if-elif structure. The default result
  is "north". Wind velocities are converted from knots (nautical miles per
  hour) to mph (statute miles per hour) by multiplying with 1.1508 and keeping
  the integer part only. 
  
  Future additions: 
    - use string formatting to report wind with 1-2 decimal digit precision.
    - convert if-elif block to a function using a dict() with 8 or even 16
      elements (to include secondary intercardinal directions), where wind 
      direction in degrees is the key and verbal description the value in the
      k-v pair.
  """
  # Conversion factor from nautical to statute (land) miles
  nautical_to_statute_mile = 1.1508
  # Initialize output string; assume invalid data
  output_string = "Invalid data!"
  # Obtain integer values from metar string
  dir, spd, gst = decode_metar_wind(wind_string)
  # Check if wind direction is legit
  if dir >=0 and dir <= 350:
    # Convert wind direction to verbal description.
    if  dir > 292:
      verbal_direction = "northwest"
    elif dir > 247:
      verbal_direction = "west"
    elif dir > 202:
      verbal_direction = "southwest"
    elif dir > 157:
      verbal_direction = "south"
    elif dir > 112:
      verbal_direction = "southeast"
    elif dir > 67:
      verbal_direction = "east"
    elif dir > 22:
      verbal_direction = "northeast"
    else:
      verbal_direction = "north"
    # Convert speed from knots to mph and take int() part only
    speed_mph = int(spd*nautical_to_statute_mile)
    # Start building output string
    output_string = ("Wind is from the " + verbal_direction + 
                     " at " + str(speed_mph) + " miles per hour")
    # Determine gusting information
    if gst is None:
      # No gusts; wrap up the output string
      output_string = output_string + "."
    else:
      # Convert gust speed from knots to mph
      gust_mph = int(gst*nautical_to_statute_mile)
      # Add gust speed to output string
      output_string = (output_string + 
                       " gusting to " + str(gust_mph) + " miles per hour.")
  # Done; return the output string
  return output_string


def assert_equal(test_expression, validation_expression):
  if test_expression == validation_expression:
    return True
  else:
    return False