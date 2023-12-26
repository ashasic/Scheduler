import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

def initialize_db():
    conn = sqlite3.connect('schedule.db')
    cur = conn.cursor()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY,
        user_id TEXT NOT NULL,
        date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL
    );
    '''
    cur.execute(create_table_query)
    conn.commit()
    conn.close()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    initialize_db()

@client.command(name='addschedule')
async def add_schedule(ctx, date, start_time, end_time):
    # Connect to SQLite3 database
    conn = sqlite3.connect('schedule.db')
    cur = conn.cursor()

    # Inserting the schedule into the database
    cur.execute("INSERT INTO schedules (user_id, date, start_time, end_time) VALUES (?, ?, ?, ?)",
                (str(ctx.author.id), date, start_time, end_time))

    # Commit and close the database connection
    conn.commit()
    conn.close()
    
    # Send a message to the channel confirming that the schedule has been added
    await ctx.send(f"Schedule added for {ctx.author.name} on {date} from {start_time} to {end_time}")

@client.command(name='addsomeone')
async def add_someone_schedule(ctx, member: discord.Member, date, start_time, end_time):
 
    conn = sqlite3.connect('schedule.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO schedules (user_id, date, start_time, end_time) VALUES (?, ?, ?, ?)",
                (str(member.id), date, start_time, end_time))
    conn.commit()
    conn.close()

    # Send a confirmation message
    await ctx.send(f"Schedule added for {member.display_name} on {date} from {start_time} to {end_time}")

@client.command(name='freetime')
async def free_time(ctx, date, check_start_time, check_end_time):

    conn = sqlite3.connect('schedule.db')
    cur = conn.cursor()

    # Find all busy times at given time
    cur.execute("SELECT user_id FROM schedules WHERE date = ? AND (start_time <= ? AND end_time >= ?)",
                (date, check_end_time, check_start_time))
    rows = cur.fetchall()

    conn.close()

    # Check if any schedules fall within given time
    if rows:
        # If schedules exist, give the name of the busy users
        user_ids = [row[0] for row in rows]
        names = [f"<@{uid}>" for uid in user_ids]
        await ctx.send(f"The following users are busy: {', '.join(names)} from {check_start_time} to {check_end_time}")
    else:
        # If no schedules conflict, everyone is free
        await ctx.send("Everyone is free at this time!")

@client.event
async def on_ready():
    print(f'{client.user} has connected')
    initialize_db()

client.run('Your discord bot ID')