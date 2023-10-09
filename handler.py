import json
import pymysql
import config 


#connection
db = pymysql.connect(host=host, user=username, passwd=password, db=db_name)

#query functions
def has_been_redeemed(code):
    cursor=db.cursor()
    cursor.execute("SELECT has_been_used FROM codes WHERE code = '{0}'".format(code))
    result = cursor.fetchall()
    return result
    #if result == 0:
     #   return False
    #else:
     #   return True

def redeem_code(code):
    cursor=db.cursor()
    cursor.execute("UPDATE codes SET has_been_used = 1 WHERE code = '{0}'".format(code))
    db.commit()

def get_usertable_id(shopify_user_id):
    cursor=db.cursor()
    cursor.execute("SELECT id FROM users WHERE shopify_user_id = '{0}'".format(shopify_user_id))
    result = cursor.fetchall()
    if result == "":
        return "DNE"
    else:
        return result

def create_user(body):
    cursor=db.cursor()
    cursor.execute("INSERT INTO users (shopify_user_id, user_email, user_firstname, user_lastname) values ('{0}', '{1}', '{2}', '{3}'".format(body['shopify_user_id'], body['user_email'], body['user_firstname'], body['user_lastname']))
    db.commit()

def write_redemption(body):
    usertable_id = get_usertable_id(body['shopify_user_id'])
    if usertable_id =="DNE":
        create_user(body)

    verified_usertable_id = get_usertable_id(body['shopify_user_id'])
    if verified_usertable_id != "DNE":
        cursor=db.cursor()
        cursor.execute("INSERT INTO redemptions (user_id, code) values ('{0}', '{1}')".format(verified_usertable_id, body['code']))
        return "Code Redeemed"
    else:
        return "ERROR: Could not write to DB"



#handle calls
def lambda_handler(event, context):
    if event['httpMethod'] == 'GET':
        pass
    if event['httpMethod'] == 'POST':
        body = json.loads(event['body'])

        #Check if the code has been redeemed before
        redemption = has_been_redeemed(body['code'])
        if redemption == 1:
            return {
                'status_code': 403,
                'body': 'Code has been redeemed already.',
                'print': json.dumps(redemption)
            }
        else:
            status = write_redemption(body)
            redeem_code(body['code'])
            return {
                'status_code': 200,
                'body': json.dumps(status)
            }
