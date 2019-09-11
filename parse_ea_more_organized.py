
# coding: utf-8

# In[7]:


import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 100) ##REMOVE IN SCRIPT


# In[6]:


def read_in_logfile(path, vid_lengths):
    pd.read_csv(path, sep='\t', skip_rows=3)
    return log_file

def get_blocks(log,vid_info):
    #identifies the video trial types (as opposed to button press events etc)
    mask = ["vid" in log['Code'][i] for i in range(0,log.shape[0])]
    #this isnt totally right lol
    #creates the dataframe with onset times and event types
    df = pd.DataFrame({'onset':log.loc[mask]['Time'], 
                  'trial_type':log.loc[mask]['Event Type'], 
                  'movie_name':log.loc[mask]['Code']})
    
    #adds trial type info
    df['trial_type']=df['movie_name'].apply(lambda x: "circle_block" if "cvid" in x else "EA_block")

    #add durations and convert them into the units here? ms??
    df['duration']=df['movie_name'].apply(lambda x: int(vid_info[x]['duration'])*10000 if x in vid_info else "n/a")

    #I don't actually know what the stim files are called for the circle ones - also these names aren't exact,gotta figure out a way to get exact file names
    df['stim_file']=df['movie_name'].apply(lambda x: vid_info[x]['stim_file'] if x in vid_info else "n/a") 
    
    
    df['end']=df['onset']+df['duration']

        
    return(df)


    
def format_vid_info(vid):
    vid.columns = map(str.lower, vid.columns)
    vid = vid.rename(index={0:"stim_file", 1:"duration"})
    vid = vid.to_dict()
    return(vid)


def read_in_standard(timing_path):
    df = pd.read_csv(timing_path).astype(str)
    df.columns = map(str.lower, df.columns)
    df_dict = df.drop([0,0]).reset_index(drop=True).to_dict(orient='list') #drops the video name
    return(df_dict)

def get_series_standard(gold_standard, block_name):
    
    return([float(x) for x in ratings_dict[block_name] if x != 'nan'])


def get_ratings(log):
    #the times in this row are EXTREMELY close to the other times. This isn't EEG, I think we're prolly ok
    rating_mask = ["rating" in log['Code'][i] for i in range(0,log.shape[0])]  
    #RT_mask=  ["Response" in log['Event Type'][i] and log['Code'][i]!="101"  for i in range(0,log.shape[0]-1)]  #this is from when i was doing it the response time way, but idk how i feel abt that

    #so now this grabs the timestamp from the row before (which is the actual onset) then applies the rating mask to that list of values
    #df = pd.DataFrame({'onset':log['Time'].shift(1).loc[rating_mask].values, 'participant_rating':log.loc[rating_mask]['Code'].values, 'event_type':'button_press', 'duration':0})    
    
    
    #switching it to not be from the row before because if it has a vid tag before it then it will get the wrong onset number
    df = pd.DataFrame({'onset':log['Time'].loc[rating_mask].values, 'participant_rating':log.loc[rating_mask]['Code'].values, 'event_type':'button_press', 'duration':0})    
    #this pretty much fixes it except for the vid_thing - one thing I could do is just get rid of the vid_ rows!! TODO later.
    
    #gets rating substring from participant numbers
    df['participant_rating'] = df['participant_rating'].str.strip().str[-1] #do i have to add a .astype to this?
    
    #TODO: probably remove this from this function and rewrite it in the place where i combine the ratings and block info
    #df['rating_duration'] = df.onset.shift(-1)-df.onset #this isnt totally correct bc of the stuff.

    return(df)


def combine_dfs(blocks,ratings):
    combo=blocks.append(ratings).sort_values("onset").reset_index(drop=True)

    mask = pd.notnull(combo['trial_type'])
    #combo['end_time']=combo['onset']-combo['onset'].shift(1)

    combo['rating_duration']=combo['onset'].shift(-1)-combo['onset'].where(mask==False) #hmm but how do i make the ones in the end of the row? because those actually should calculate from block_end, not from the beginning of the next guy...
    #this one is tricky!!

    block_start_locs=combo[mask].index.values

    #so one way to do this would be to make durations visible everywhere

    #can i do for i in block_start_locs

    #yay! fixes the rating for the last button press of a series!
    #gives a SettingWithCopy warning
    #TODO: fix this lol
    #this ends up not assigning a value for the final button press - there must be a more elegant way to do all this
    for i in range(len(block_start_locs)):
        if block_start_locs[i] != 0:
            #maybe i should calculate these vars separately for clarity
            combo.rating_duration[block_start_locs[i]-1]=combo.end[block_start_locs[i-1]] - combo.onset[block_start_locs[i]-1]

            
#adds rows that contain the 5 second at the beginning default value
    for i in block_start_locs:
            new_row={'onset':combo.onset[i],
            'rating_duration':combo.onset[i+1] - combo.onset[i],
            'event_type':'default_rating',
            'duration':0,
            'participant_rating':5}
            combo=combo.append(new_row,ignore_index=True)
        
    combo=combo.sort_values("onset").reset_index(drop=True)

    return(combo)


# In[9]:


#Reads in the log, skipping the first three preamble lines
log=pd.read_csv('/projects/gherman/Experimenting_notebooks/SPN01_CMH_0001-UCLAEmpAcc_part1.log', sep='\t', skiprows=3)


vid_in = pd.read_csv('EA-vid-lengths.csv')

vid_info = format_vid_info(vid_in)
blocks = get_blocks(log, vid_info)
ratings = get_ratings(log)

#add the ratings and the block values together, then sort them and make the index numbers sequential
combo=combine_dfs(blocks,ratings)


# In[ ]:


mask = pd.notnull(combo['trial_type']) #selects the beginning of trials/trial headers
block_start_locs=combo[mask].index.values

block_start=combo.onset[block_start_locs[0]]
block_end=combo.end[block_start_locs[0]]

#selects the rows between the start and the end that contain button presses
block = combo[combo['onset'].between(block_start, block_end) & pd.notnull(combo.event_type)] #between is inclusive by default
block_name= combo.movie_name[combo['onset'].between(block_start, block_end) & pd.notnull(combo.movie_name)].astype(str).get(0) 
###############################################################################################

interval = np.arange(combo.onset[block_start_locs[0]], combo.end[block_start_locs[0]],step=20000)


interval=np.append(interval, block_end) #this is to append for the remaining fraction of a second - maybe i dont need to do this

#why is this not doing what it is supposed to do.
#these ifs are NOT working
two_s_avg=[]
for x in range(len(interval)-1):
    start=interval[x]
    end=interval[x+1]
    #things that start within the time interval plus the one that starts during the time interval
    sub_block= block[block['onset'].between(start,end) | block['onset'].between(start,end).shift(-1)]
    block_length=end-start
    if len(sub_block) !=0: 
        ratings=[]
        last_val=sub_block.participant_rating.iloc[[-1]]
        for index, row in sub_block.iterrows():
            #for rows that are in the thing
            if (row.onset < start): #and (row.onset+row.duration)>start: #what's the best order to do these conditionals in?
                #if (row.onset+row.duration)>start: # this is just to be safe i guess, gonna see what happens if i comment it out
                numerator=(row.onset+row.rating_duration)-start
            else:#if row.onset>=start and row.onset<end: #ooo should i do row.onset<end for everything??
                if (row.onset+row.rating_duration) <= end:
                    numerator=row.rating_duration
                elif (row.onset+row.rating_duration) > end: 
                    numerator = end - row.onset
                else:
                    numerator=9999999
            last_row=row.participant_rating
            #okay so i want to change this to actually create the beginnings of an important row in our df!
            ratings.append({'start':start,'end':end,'row_time':row.rating_duration, 'row_start': row.onset, 'block_length':block_length,'rating':row.participant_rating, 'time_held':numerator})#, 'start': start, 'end':end})
            nums=[float(d['rating']) for d in ratings]
            times=[float(d['time_held'])/block_length for d in ratings]
            avg=np.sum(np.multiply(nums,times))
    else:
        avg=last_row
    
    #okay so i want to change this to actually create the beginnings of an important row in our df!
    two_s_avg.append(float(avg))
    
    

gold_standard=[float(x) for x in ratings_dict[block_name] if x != 'nan']
    

