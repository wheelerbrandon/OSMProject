# Function to have phone numberattribute follow Open Street Map guidelines
# helper function for simplifying phone number update...
# slices cleaned phone number into ordered breaks, rejoins together with '-'
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

#function for fixing postcode attribute
#removes non numeric characters and limits to 5 digits
def update_zip(zip_code):
    temp = ''
    # Use regular expressions to develop temp string based on only NUMBERS from phone_number
    for i in range(len(zip_code)):
        match = re.search(r'[0-9]', zip_code[i])
        if match:
            temp = temp + match.group()
    if len(temp) == 5:
        fixedzip = temp
    #if length greater than 5,
    #just take the first 5 digits
    #simple way to fix hyphenated zipcodes
    elif len(temp) > 5:
        fixedzip = temp[0:5]
    return fixedzip

# function + mapping for fixing street name attrubte
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
            "AVE" : "Avenue"
            }
def update_street_name(name, mapping):
    # split streetname into list
    fixed_name = name.split(" ")
    # correctable street types come at the end,
    # so this can be taken advantage of for cleaning
    # replace street value based on mapping
    if fixed_name[-1] in mapping:
        fixed_name[-1] = mapping[fixed_name[-1]]
    # rejoin on a " "
    name = " ".join(fixed_name)
    return name

# function + mapping for fixing state attribute
state_mapping = {"VIRGINIA" : "VA",
           "virginia" : "VA",
           "va" : "VA",
           "Va" : "VA"
          }

def update_state(name, mapping):
    fixedstate = ''
    if name in mapping:
        fixedstate = mapping[name]
        return fixedstate
    else:
        return name


# function + mapping for fixing city attribute
city_mapping = {"NORFOLK" : "Norfolk",
          "VIRGINIA BEACH" : "Virginia Beach",
          "CHESAPEAKE" : "Chesapeake",
          "HAMPTON" : "Hampton",
          "PORTSMOUTH" : "Portsmouth",
          "Noroflk" : "Norfolk",
          "hampton" : "Hampton"}
def update_city(name, mapping):
    fixedcity = ''
    if name in mapping:
        fixedcity = mapping[name]
        return fixedcity
    else:
        return name

# function + mapping for fixing state attribute
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
