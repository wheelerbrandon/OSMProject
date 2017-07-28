
# OpenStreetMap Data Case Study

### Map Area
Norfolk, VA, United States

- [https://www.openstreetmap.org/relation/206672]()

I spent my teenage years in neighboring suburb Chesapeake, but I thought that Norfolk, being a city, would have a greater quantity of data to clean, as well as more interesting data to assess afterwards. Norfolk is a coastal city in Virginia, famouse for it's shipyards, ties to the navy, and home of Doumar's- a burger joint where the ice cream cone was supposedly invented!

## Problems Encountered in the Map
Upon receiving the XML data and having difficulty opening it in Atom due to it's size(401 mb), I created a programmatically sliced sample of the data (taking every 10th top level element) to develop initial assessments.

On inspection, the data seemed quite clean, but there were some exceptions.

- Street address information was typically written correctly (Street, Circle, Road etc.) but sometimes abbreviated.
- OSM guidelines indicate "state" should be indicated with the capitalized abbreviation (VA) but the entries lacked uniformity (Virginia, virginia, va, Va, etc.)
- Entries including city information would sometimes be in all-caps (CHESAPEAKE, HAMPTON, etc.) or misspelled (Noroflk), additionally, wasn't this just supposed to be Norfolk?
- More unique postcodes were in the data then expected, and some postcodes were prefixed with the state (VA23402), and others were hyphenated without cause (23322-24023)
- Phone numbers had little uniformity, (7573216683, 1757-223-8838, etc.) and did not reflect OSM guidelines to follow the +1-XXX-XXX-XXXX format

### Over­abbreviated Street Names
After parsing addr:street values from the sample and seeing what types of errors existed, I made a dictionary to reference for correcting those abbreviations, as well as what I could expect to appear in the full OSM file. Because these street types appear at the end of an address, my function for correcting a street names splits the address string and checks if the final portion is inside the mapping dictionary, which would warrant correction.

```python 
street_mapping = { "St.": "Street",
            "St" : "Street",
            "ST" : "Street",
            "ST." : "Street",
            "street" : "Street",
            "Rd" : "Road",
            "RD" : "Road",
            "Rd." : "Road",
            "RD." : "Road",
            "Ave" : "Avenue",
            "AVE" : "Avenue",
            "Ave." : "Avenue"
            }

def update_street_name(name, mapping):
    fixed_name = name.split(" ")
    if fixed_name[-1] in mapping:
        fixed_name[-1] = mapping[fixed_name[-1]]
    name = " ".join(fixed_name)
    return name
```

### City & State Errors
Because these tags are significantly less commonly listed by users than addr:street, it was easier to create mapping dictionaries to ensure all errors in the data are corrected, and because they're single word tags, simpler to correct as well.

```python 
#City mapping dictionary + update function 
city_mapping = {"NORFOLK" : "Norfolk",
          "VIRGINIA BEACH" : "Virginia Beach",
          "CHESAPEAKE" : "Chesapeake",
          "HAMPTON" : "Hampton",
          "PORTSMOUTH" : "Portsmouth",
          "Noroflk" : "Norfolk",
          "hampton" : "Hampton"
          }
          
def update_city(name, mapping):
    fixedcity = ''
    if name in mapping:
        fixedcity = mapping[name]
        return fixedcity
    else:
        return name

#State mapping dictionary + update function
state_mapping = {"VIRGINIA" : "VA",
           "virginia" : "VA",
           "va" : "VA",
           "Va" : "VA",
           "Virginia" : "VA"
          }
          
def update_state(name, mapping):
    fixedstate = ''
    if name in mapping:
        fixedstate = mapping[name]
        return fixedstate
    else:
        return name
```

### Postal Code Errors
Observing that postal codes had issues both with unnecessary prefixes and suffixes, it was clear that an elegant solution would be to slice out the relevant 5 number code and leave the rest behind.
```python 
def update_zip(zip_code):
    temp = ''
    # Use regular expression to isolate numeric characters
    for i in range(len(zip_code)):
        match = re.search(r'[0-9]', zip_code[i])
        if match:
            temp = temp + match.group()
    if len(temp) == 5:
        fixedzip = temp
    #if length greater than 5,
    #just take the first 5 digits
    elif len(temp) > 5:
        fixedzip = temp[0:5]
    return fixedzip    
```

## Phone Number Errors
Observing that Open Street Map has a preferred syntax for how phone numbers should be written, I decided that I should write a function using regular expressions and slicing that can take any format and convert to the correct one.

```python 
# Helper function for slicing and rejoining phone numbers
# Slices at International extension, local extension, first 3 digits, last 4 digits,
# joins slices with a hyphen
def slice_and_join(temp):
    slices = []
    slices.append(temp[0:2])
    slices.append(temp[2:5])
    slices.append(temp[5:8])
    slices.append(temp[8:12])
    number = "-".join(slices)
    return number
    
    
def update_phone(phone_number):
    temp = ''
    number = ''
    # Use regular expressions to develop temp string based on only NUMBERS from phone_number
    for i in range(len(phone_number)):
        match = re.search(r'[0-9]', phone_number[i])
        if match:
            temp = temp + match.group()
    # Use length of string to determine what information is missing
    # i.e., if length is 10, that means the international extension is missing
    # so add it!
    if len(temp) == 10:
        temp = '+1' + temp
        number = slice_and_join(temp)
    # if length is 11, check to make sure it's leading with a 1
    # if not, correct the number
    elif len(temp) == 11:
        if temp[0] == '1':
            temp = '+' + temp
            number = slice_and_join(temp)

        else:
            temp = '+1' + temp[1:]
            number = slice_and_join(temp)

    # if phone number is some other length...
    # can use local knowledge to fix, take last 7 digits
    # and add the local area code + international extension
    else:
        slices = []
        temp = temp[-7:]
        slices.append('+1')
        slices.append('757')
        slices.append(temp[0:3])
        slices.append(temp[3:7])
        number = "-".join(slices)

    return number
```

## Cities & Postcodes?
As I mentioned earlier, it seemed odd that I was seeing Hampton, Portsmouth, Chesapeake, etc. in the cities tags, as well as a larger variety of postcodes than the expected 25. Was it possible the extent covered more area than I anticipated?

```sql
# Instances of cities in dataset

SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='cities'
GROUP BY tags.value
ORDER BY count DESC;

City            Count
Norfolk         79762
Virginia Beach  44250
Hampton         24990
Chesapeake       8756
Portsmouth         14


# Distinct Postcodes?

SELECT COUNT(DISTINCT(tags.value))
FROM (SELECT value, key FROM nodes_tags 
	  UNION ALL 
      SELECT value, key FROM ways_tags) tags
WHERE tags.key='postcode';

32
```

It appears that in the process of developing a custom extent at my request, Open Street Map delivered a much larger portion of the Hampton Roads area than I expected. For this project it's not an issue, but something to be wary of if one really wished to hone in an area to clean up.

# Data Overview and Additional Ideas

This section contains auxiliary info on the completed dataset, what queries I came up with to examine it, and some bonus stuff.


### File sizes
```
Norfolk.osm ........... 401 MB
Norfolk.db ............ 231 MB
nodes.csv ............. 168 MB
nodes_tags.csv ........ 0.53 MB
ways.csv .............. 13 MB
ways_tags.csv ......... 32 MB
ways_nodes.cv ......... 46 MB  
```  

### Number of nodes
```
sqlite> SELECT COUNT(*) FROM nodes;
```
1698776

### Number of ways
```
sqlite> SELECT COUNT(*) FROM ways;
```
196651

### Number of unique contributing users
```sql
sqlite> SELECT COUNT(DISTINCT(e.uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;
```
343

### Top 10 contributing users
```sql
sqlite> SELECT both.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) both
GROUP BY both.user
ORDER BY num DESC
LIMIT 10;
```

```sql
jonahadkins_norfolk_imports|799317
jonahadkins_vabeach_imports|345147
jonahadkins_hampton_imports|219340
Jonah Adkins               |197702
Omnific                    |105057
woodpeck_fixbot            |83940
CynicalDooDad              |28848
jumbanho                   |14605
SumnerDo 01                |10573
42429                      |10558
```

### Number of users appearing only once (having 1 post)
```sql
sqlite> SELECT COUNT(*) 
FROM
    (SELECT both.user, COUNT(*) as num
     FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) both
     GROUP BY both.user
     HAVING num=1)  u;
```
57

### Observations & Additional Ideas
The top 4 contributing users appear to all be separate accounts belonging to one, Jonah Adkins. They are responsible for 1561506 contributions out of 1895427 total which equates to 82.38%(!!!) of all data in the extent.

However, it's worth noting that 3 of Jonah's usernames are tagged with 'imports'. Perhaps Jonah has data from other databases made compatible for OSM? A cursory search indicates that Jonah is a [geospatial specialist](http://jonahadkins.com) from Newport News, VA - the perfect candidate of who might be a devout OSM contributor.

The fact that it was somewhat diffiult for me to initially find data to clean seems more reasonable now that I know a geospatial data professional has taken a personal interest in the area. This leads me to wondering, although OSM is a free and crowd sourced, perhaps a method to improve data quality all over the world would be to offer geospatial experts incentives to "adopt" areas, similar to how localities allow citizens to do with highways and roads. Encouraging users to become the steward of a small area of the map, on the level of a neighborhood or something similar, could provide a level of ownership or attachment that will improve how users interact with data at the micro level. This method would work best if contributors in a region were uniformly distributed, but as that is not guaranteed it may encourage a trend of very high quality pockets of data where portions of the map have been adopted, with significant drop off elsewhere. If this avenue of encouragement using sentimentality is not enough, perhaps pursuing gamification is an appropriate response. 

Services such as FourSquare and Swarm have used gamification and managed to develop fairly detailed consumer profiles by offering users rewards in the form of virtual badges and stickers. Furthermore, they encourage diligent app usage by setting up user competitions to engage local businesses, parks, and landmarks by crowning the most active user at a location the "Mayor". Perhaps Open Street Map could adopt this approach, by rewarding the most active contributors to a county's dataset similar titles. I would anticipate this type of system working better in highly populated areas, where the presence of many competing users could create a profound impact on the quality of the dataset. In less populated areas with fewer users overall as well as a population less interested in a virtual competition however, these efforts would likely be significantly less effective.

## Additional Data Exploration

### Do any phone numbers appear multiple times?

```sql
sqlite> SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='phone'
GROUP BY tags.value
ORDER BY count DESC
limit 5;

+1-757-857-3340|13
+1-757-466-7683|2
+1-757-490-1111|2
+1-757-727-0900|2
+1-336-391-9884|1
```

One phone number appears attached to 13 records somehow! Let's see what records it's attached to for an explanation,

```sql
sqlite> SELECT id
FROM nodes 
WHERE id IN (SELECT DISTINCT(id) FROM nodes_tags WHERE key='phone' 
AND value='+1-757-857-3340');

3684647708
3684647709
3684647710
3684647711
3684647712
```

5 subsequent nodes based on IDs, indicating the records were made one after another. What kind of amenity is it?

```sql
sqlite> SELECT * FROM nodes_tags WHERE id=3684647712;

3684647712|fee|yes|regular
3684647712|name|Short-Term Parking|regular
3684647712|phone|+1-757-857-3340|regular
3684647712|access|customers|regular
3684647712|amenity|parking|regular
3684647712|parking|multi-storey|regular
3684647712|supervised|yes|regular

sqlite> SELECT * FROM nodes_tags WHERE id=3684647708;

3684647708|fee|yes|regular
3684647708|name|Long-Term Parking|regular
3684647708|phone|+1-757-857-3340|regular
3684647708|access|customers|regular
3684647708|amenity|parking|regular
3684647708|parking|multi-storey|regular
3684647708|supervised|yes|regular
```

After reviewing each node, it appears to be a multi-story parking facility that offers short-term, long-term, oversized short-term, and oversized long-term parking, each sharing the same front desk phone number. Interesting!

## Amenity Breakdown

Some of the more interesting data to examine are the amenities, as they give more sense to the character of the area than other categories might. However, it's important to reiterate here that because it's only based on what data has been implemented in the OSM file, it may not be entirely accurate! Anyways,

```sql
sqlite> SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10;

place_of_worship|164
school          |103
fast_food       |73
restaurant      |60
fuel            |37
cafe            |18
fire_station    |17
fountain        |14
police          |14
post_office     |13
```

I was surprised that religious sites outnumbered all other amenities- even if fast_food, restaurant, and cafe weren't separated, they would be outnumbered by places of worship.

### Places of Worship

How do the places of worship break down?

```sql
sqlite> SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='place_of_worship') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='religion'
GROUP BY nodes_tags.value
ORDER BY num DESC;

christian |158
jewish    |  2
```

Only 2 non-Christian places of worship were labeled, with 4 records not having a value field at all.

### Fast Food

What's the makeup of the fast food choices?

```sql
sqlite> SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='fast_food') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='name'
GROUP BY nodes_tags.value
ORDER BY num DESC
Limit 10;

Subway          |9
Burger King     |5
Wendys          |5
Taco Bell       |3
Chick-fil-A     |2
KFC             |2
McDonalds       |2
Schlotzskys Deli|2
A&W             |1
Baskin-Robbins  |1
```

Subway holds a significant lead in quantity from the database, which is somewhat surprising to me. I'm quite convinced that, for some unknown reason OSM useres were more likely to include Subway in their contributions. Perhaps someone from Subway coprorate had taken notice of the resource?!

# Conclusion
Although the amount of user contributions of data for the greater Norfolk area impressed me initially with both the volume and quality, after examining the database further with SQLite, it became obvious how incomplete it was. I am, however, proud of the automated fixes to the data I was able to make and I was pleased to see that all the methods I developed were successful in cleaning the data in the manner I designed them to. Unfortunately, in order to truly improve the data in Norfolk cleaning isn't the real issue, the data requires significantly more input in terms of tags and descriptors- perhaps encouraging the "adoption" and stewardship of neighborhoods and smaller areas, or taking a deeper approach towards gamification would provide significant improvements.


```python

```
