from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from schemas import *
from sqlalchemy.orm import Session
from fastapi import Depends, status
from database import DATABASE_URL, get_db
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

db = []

@app.get('/', status_code=HTTPStatus.OK, response_model=Message) 
def read_root():
    return {'message':'Running...'}

# ---------------------------------------- TESTE FastAPI ----------------------------------------
'''
@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):

    user_id = UserDB(
        id=len(db)+1, 
        **user.model_dump())
    db.append(user_id)

    return user_id

@app.get('/users/', response_model=UserList)
def read_users():
    return {'users': db}

@app.put('/users/{u_id}', response_model=UserPublic)
def update_user(u_id: int, user: UserSchema):

    if u_id < 1 or u_id > len(db):
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')

    user_id = UserDB(
        id=u_id,
        **user.model_dump())
    db[u_id-1] = user_id

    return user_id

@app.delete('/users/{u_id}')
def delete_user(u_id: int):
    if u_id < 1 or u_id > len(db):
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')
    db.pop(u_id-1)

    return {'message': f'user {u_id} deleted'}
'''
# ------------------------------------------------------------------------------------------------

# --------------------------------------- TESTE PostgreSQL ---------------------------------------

@app.get('/checkpg/')
def healthcheck(db: Session = Depends(get_db)):
    try:     
        db.execute(text('SELECT 1'))
        return {'status': 'ok'} 
    except Exception as e:        
        raise HTTPException( 
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail='Database health check failed: ' + str(e) )

@app.get('/readpg/')
def read_table_pg():
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users;')
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {'data': rows}
    except Exception as e:
        return {'error': str(e)}

@app.post('/postpg/')
def create_user_pg(user: UserPG):
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()

        insert_query = 'INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING *;'
        cursor.execute(insert_query, (user.username, user.email, user.password))
        
        new_user = cursor.fetchone()
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {'message': 'SUCCESS: Created user!', 'user': new_user}
    except Exception as e:
        return {'error': str(e)}

@app.delete('/deletepg/{username}')
def delete_user_pg(username: str):
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = %s;', (username,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail='User not found!')

        delete_query = 'DELETE FROM users WHERE username = %s RETURNING *;'
        cursor.execute(delete_query, (username,))
        deleted_user = cursor.fetchone()
        conn.commit()

        cursor.close()
        conn.close()

        return {'message': 'SUCCESS: Deleted user!', 'user': deleted_user}
    except Exception as e:
        return {'error': str(e)}
    
@app.put('/updatepg/{username}')
def update_user_pg(username: str, user_update: UserUpdatePG):
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = %s;', (username,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail='User not found!')

        update_fields = []
        update_values = []

        if user_update.username:
            update_fields.append('username = %s')
            update_values.append(user_update.username)

        if user_update.email:
            update_fields.append('email = %s')
            update_values.append(user_update.email)

        if user_update.password:
            update_fields.append('password = %s')
            update_values.append(user_update.password)

        if not update_fields:
            raise HTTPException(status_code=400, detail='No data for update.')

        update_query = f'UPDATE users SET {', '.join(update_fields)} WHERE username = %s RETURNING *;'
        update_values.append(username)
        cursor.execute(update_query, tuple(update_values))
        updated_user = cursor.fetchone()
        conn.commit()

        cursor.close()
        conn.close()

        return {'message': 'SUCCESS: Updated user!', 'user': updated_user}
    except Exception as e:
        return {'error': str(e)}

# ------------------------------------------------------------------------------------------------
