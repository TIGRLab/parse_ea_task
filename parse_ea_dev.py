
# coding: utf-8

# In[42]:


import pandas as pd
import numpy as np


# In[63]:


def read_in_logfile(path, vid_lengths):
    pd.read_csv(path, sep='\t', skip_rows=3)


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
        
    return(df)

    
def format_vid_info(vid):
    vid.columns = map(str.lower, vid.columns)
    vid = vid.rename(index={0:"stim_file", 1:"duration"})
    vid = vid.to_dict()
    return(vid)



def get_ratings(log):
    #the times in this row are EXTREMELY close to the other times. This isn't EEG, I think we're prolly ok
    rating_mask = ["rating" in log['Code'][i] for i in range(0,log.shape[0])]  
    #RT_mask=  ["Response" in log['Event Type'][i] and log['Code'][i]!="101"  for i in range(0,log.shape[0]-1)]  #this is from when i was doing it the response time way, but idk how i feel abt that

    #so now this grabs the timestamp from the row before (which is the actual onset) then applies the rating mask to that list of values
    df = pd.DataFrame({'onset':log['Time'].shift(1).loc[rating_mask].values, 'participant_rating':log.loc[rating_mask]['Code'].values, 'event_type':'button_press', 'duration':0})    
    
    #TODO: probably remove this from this function and rewrite it in the place where i combine the ratings and block info
    #df['rating_duration'] = df.onset.shift(-1)-df.onset #this isnt totally correct bc of the stuff.

    return(df)



# In[74]:


#Okay let's try figuring out something w adding in the gold standard ratings...

#what if i make an extra column in the logs for time elapsed in video, and then find out which rating it should get by dividing by two

#[x for x in combo['trial_type'] if x]
#if combo['trial_type']:
#    print(combo['trial_type'])

combo.isna()


# In[147]:


#Reads in the log, skipping the first three preamble lines
log=pd.read_csv('/projects/gherman/Experimenting_notebooks/SPN01_CMH_0001-UCLAEmpAcc_part1.log', sep='\t', skiprows=3)


vid_in = pd.read_csv('EA-vid-lengths.csv')
vid_info = format_vid_info(vid_in)
blocks = get_blocks(log, vid_info)
ratings = get_ratings(log)

#add the ratings and the block values together, then sort them and make the index numbers sequential
combo=blocks.append(ratings).sort_values("onset").reset_index(drop=True)
combo
#find what index each block starts and ends at, then does some stupid formatting stuff to flatten the array
t=np.array(np.where(pd.notnull(combo['trial_type']))).ravel()

#adds the end of the last trial
t = np.append(t,len(combo["trial_type"])-1)
#but this doesnt capture the end of the last trial... how do i make it do that??

#creates a dict with trials and start/ends. Next it needs to differentiate between circles and EA and then get the nice values.
[{(combo['trial_type'][t[i]],combo['stim_file'][t[i]]): {'start':t[i],'end':t[i+1]-1}} for i in range(len(t)-1)]

#(combo['trial_type'][t[0]],combo['trial_type'][t[1]-1])
#pd.notnull(combo['trial_type'])
#(starts,ends)=[(t[i],t[i+1]-1) for i in range(len(t)-1)]

#combo.sort_values("onset")
#uses isna in some versions
#combo.isnull()

#combo.sort_values("onset")


#log['Time']=log['Time'].astype(str) #can i read it in initially with strings only? like stringsAsFactors=T in R?

#Finds the start and end times of blocks


#okay so Time from row n-1 + TTime from row n = Time in row n !!! 
#We will subtract Duration of MRI start from all times to give us the time
#(block_starts, block_types) = (log['Time'][] 
                               
 #                              df.loc[df['B'], 'A']

#f['c2'] = df['c1'].apply(lambda x: 10 if x == 'Value' else x)

#def get_button_press(log):

#Time col contains the button press onset time in event_type=response, Code col 
#contains the button press' value in rating_mask

#101 is the event code for some initial button press or response. We can ignore it. (AT LEAST acc. to the CAMH
#scan. Please cross-reference with others before finalizing)

#log['Time'] = log['Time'].astype(str)
#rating_mask = ["rating" in log['Time'][i] for i in range(0,log.shape[0]-1)]  
#response_mask=  ["rating" in log['Code'][i] for i in range(0,log.shape[0]-1)]  

#or "Response" in log['Code'][i]
    
#df = pd.DataFrame({'onset':log.loc[rating_mask]['Time'], 'rating':log.loc[response_mask]['Code']})    

#df
    
#pd.DataFrame{'col1': [1, 2], 
           #  'col2': [3, 4]}

#[[log['Code'][i], log['Time'][i], log['Event Type'][i]] for i in range(0,log.shape[0]-1) if("vid" in log['Code'][i])]


# In[19]:



#Time col contains the button press onset time in event_type=response, Code col 
#contains the button press' value in rating_mask

#I am not entirely sure that I should be getting the time from the row before, but it kind of makes sense to take the most straightforward one

#101 is the event code for some initial button press or response. We can ignore it. (AT LEAST acc. to the CAMH
#scan. Please cross-reference with others before finalizing)


#the times in this row are EXTREMELY close to the other times. This isn't EEG, I think we're prolly ok
rating_mask = ["rating" in log['Code'][i] for i in range(0,log.shape[0])]  
#RT_mask=  ["Response" in log['Event Type'][i] and log['Code'][i]!="101"  for i in range(0,log.shape[0]-1)]  #this is from when i was doing it the response time way, but idk how i feel abt that

#so now this grabs the timestamp from the row before (which is the actual onset) then applies the rating mask to that list of values
df = pd.DataFrame({'onset':log['Time'].shift(1).loc[rating_mask].values, 'participant_rating':log.loc[rating_mask]['Code'].values, 'event_type':'button_press', 'duration':0})    

df['rating_duration'] = df.onset.shift(-1)-df.onset #this isnt totally correct bc of the stuff.



# In[57]:


df2=blocks.append(df)

df2.sort_values("onset")

log

rating_mask = ["rating" in log['Code'][i] for i in range(0,log.shape[0])]  
log['Time'].shift(1).loc[rating_mask].values


# In[56]:


rating_mask = ["rating" in log['Code'][i] for i in range(0,log.shape[0])]  
log['Time'].shift(1).loc[rating_mask]


# In[34]:


vid_lengths = pd.read_csv('EA-vid-lengths.csv')
vid_lengths.columns = map(str.lower, vid_lengths.columns)
vid_lengths = vid_lengths.rename(index={0:"stim_file", 1:"duration"})
vid_lengths = vid_lengths.to_dict()






mask = ["vid" in log['Code'][i] for i in range(0,log.shape[0]-1)]
    #this isnt totally right lol
df = pd.DataFrame({'onset':log.loc[mask]['Time'], 
                  'trial_type':log.loc[mask]['Event Type'], 
                  'movie_name':log.loc[mask]['Code']})
    
df['trial_type']=df['movie_name'].apply(lambda x: "circle_block" if "cvid" in x else "EA_block")

#add durations and convert them into the units here? ms??
df['duration']=df['movie_name'].apply(lambda x: int(vid_info[x]['duration'])*10000 if x in vid_info else "n/a")

#I don't actually know what the stim files are called for the circle ones - also these names aren't exact
df['stim_file']=df['movie_name'].apply(lambda x: vid_info[x]['stim_file'] if x in vid_info else "n/a")


