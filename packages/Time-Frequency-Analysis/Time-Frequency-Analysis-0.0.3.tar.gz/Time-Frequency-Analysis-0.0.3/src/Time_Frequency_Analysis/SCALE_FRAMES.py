
import numpy as np
import scipy
from numpy.fft import rfft,irfft
import os
import time
import librosa
from Audio_proc_lib.audio_proc_functions import * 
import multiprocessing
import scipy.signal as sg




class scale_frame:

    #FOR THE IMPLEMENTATION OF THE IRREGULAR MATRIX i assumed that Ln (window len) = Mn (FFT len)  
    #Painless case Ln<=Mn


    #CONSTRUCTOR PARAMETERS
    #1)ksi_s : sampling rate
    #2)min_scl : minimal scale given in samples
    #3)overlap_factor : the amount of overlap each new constructed window will have to its previous one (and the next one) given as a ratio
    #   Notes-> i.e. overlap_factor of 1/2 means that if the previous window is 512samples then the next one will overlap in 256samples (similar to hop size in STFT)
    #           For the first and the last windowes we used a tukey window and an overlap of 1/2 .
    #4)onset_seq : The sequence of onsets produced by an onset detection algorithm
    #5)middle_window : The middle window used in each get_window_interval procedure given as an object i.e. np.hanning or scipy.signal.tukey  
    #6)L : signal length in samples
    #7)matrix_form : flag to indicate if will be calculated a regular matrix or irregular matrix     
    #8)multiproc : flag to indicate if it will use multiprocessing to compute the window for each onset interval indices in the get_window_interval procedure 
    # (recommended True)          

    def timeis(func):
        '''Decorator that reports the execution time.'''
  
        def wrap(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            
            print(func.__name__, end-start)
            return result
        return wrap
    
    def cputime(self):
        utime, stime, cutime, cstime, elapsed_time = os.times()
        return utime    


    g = []
    g_dual = []


    def __init__(self,ksi_s,min_scl,overlap_factor,onset_seq,middle_window,L,matrix_form,multiproc):
        self.ksi_s = ksi_s
        self.onsets = onset_seq
        self.min_scl=min_scl
        self.overlap_factor = overlap_factor
        self.multiprocessing = multiproc
        self.middle_window = middle_window
        self.L=L
        self.matrix_form=matrix_form
        #writing in the correct order the function calls in order for the FORWARD AND BACKWARD methods to work

        #Creating the onset_tuples sequence
        self.get_onset_tuples()

        #Construction of the windows indices
        if self.multiprocessing:
            pool = multiprocessing.Pool(processes=4)
            all_inds_list = list( pool.imap(self.get_windows_interval, self.onset_tuples) )
        else:
            all_inds_list = list( map( lambda x : self.get_windows_interval(x) , self.onset_tuples ) )
        
        self.all_inds = []
        for interval_inds in all_inds_list:
            self.all_inds += interval_inds

        self.get_first_last_window()      

        self.N = len(self.all_inds)

        self.get_frame_operator()







    

    def get_onset_tuples(self):

        #onsets = librosa.onset.onset_detect(y=sig, sr=self.ksi_s, units="samples")
        #putting manualy some onsets in the start and the end 
        #and then creating a sequence of onset tuples (each tuple contains two successive onsets)
        self.onsets = np.insert( self.onsets , [0,len(self.onsets)] , [self.min_scl,(self.L-1)-self.min_scl] ) 
        self.onset_tuples = []
        for i in range(len(self.onsets)-1):
            self.onset_tuples.append( (self.onsets[i],self.onsets[i+1]) )                   


    def get_windows_interval(self,onset_tuple):
        #Function to get the window start (a) , end (b) indices and window length 
        #for the windows between 2 onsets 

        #Params:
        #1)onsets_tuple: the first and last onset for the interval under considaration
        #2)self.min_scl: is the minimal scale that we apply to the two onsets (because they are the transient positions) (POWER OF 2)
        #3)overlap_fact: the amount of the previous window that the next will overlap to the previous (must be a fraction greater than 1)    

        #Idea implemented:
        #In the first onset we use the minimal scale and for the following windows we increase the scale by doubling it each time
        # until the median (end + start)/2  of the interval . We use the symmetric windows in order to reash gradually the minimal 
        # scale again in the position of the second onset. For the median position we use another window.
        #
        
         

        #Constructing the windows for all onset intervals-----------------------------------------------------------------------------------
        start = onset_tuple[0]
        end = onset_tuple[1]
        middle = (start + end )//2 
        win_len = self.min_scl


        #Constructing the first symmetric windows--------------------------------------------------------------------
        inds_dict = [ { "window" : np.hanning , "win_len" : win_len , "a" : start - win_len//2 , "b" : start + win_len//2  } ]

        k = 0
        while True:
            k+=1

            ovrlp = int(inds_dict[k-1]["win_len"]*self.overlap_factor)    

            window = np.hanning
            win_len = win_len*2
            a = inds_dict[k-1]["b"] - ovrlp
            b = a + win_len


            if b>middle:
                break
            # if (a+b)/2>middle:
            #     break
            else:
                inds_dict.append( { "window" : window , "win_len" : win_len , "a" : a , "b" : b  } )
                    

        #Constructing the middle window---------------------------------------------------------------------------------------
        window = self.middle_window
        ovrlp = int(inds_dict[-1]["win_len"]*self.overlap_factor)
        a = inds_dict[-1]["b"] - ovrlp
        b = int( 2*middle - inds_dict[-1]["b"] ) + ovrlp
        win_len = b - a
        inds_dict.append( { "window" : window , "win_len" : win_len , "a" : a , "b" : b  } )



        #Constructing the first symmetric windows --------------------------------------------------------------------------------
        # (we dont need the last symmetric window thats why the for loop goes until 0 )
        for k in range(len(inds_dict)-2,0,-1):
            tmp = inds_dict[k].copy()
            tmp["a"] = int( 2*middle - inds_dict[k]["b"] )
            tmp["b"] = int( 2*middle - inds_dict[k]["a"] )
            inds_dict.append(tmp)

            
        
        return inds_dict



    def get_first_last_window(self):

            
        #first_window
        ovrlp = int(self.all_inds[0]["win_len"]*self.overlap_factor)
        ovrlp = int(self.all_inds[0]["win_len"]*(1/2))
        a = 0
        b = self.all_inds[0]["a"] + ovrlp
        win_len = b - a
        first_window_inds = { "win_len" : win_len , "a" : a , "b" : b } 

        #last_window
        #ovrlp = int(self.all_inds[len(self.all_inds)-1]["win_len"]*self.overlap_factor)
        ovrlp = int(self.all_inds[len(self.all_inds)-1]["win_len"]*(1/2))
        a = self.all_inds[len(self.all_inds)-1]["b"] - ovrlp
        b = self.L 
        win_len = b - a
        last_window_inds = { "win_len" : win_len , "a" : a , "b" : b }     

        self.all_inds = [first_window_inds] + self.all_inds + [last_window_inds] 

        
    def plot_windows(self):
        #Plot the windows for a small 3sec exerpt of the signal  

        if self.L/44100<7:
            #first window using Tukey
            z_tmp = np.zeros(self.L)
            inds = np.arange( self.all_inds[0]["a"],self.all_inds[0]["b"] )            
            Ln = self.all_inds[0]["win_len"]
            gn = np.roll( sg.tukey( Ln*2 ) , Ln )[:Ln]
            z_tmp[inds] = gn
            plt.plot(z_tmp)

            for k in range(1,self.N-1):
                z_tmp = np.zeros(self.L)
                inds = np.arange( self.all_inds[k]["a"],self.all_inds[k]["b"] )
                z_tmp[inds] = self.all_inds[k]["window"]( self.all_inds[k]["win_len"] )
                plt.plot(z_tmp)

            #last window using Tukey
            z_tmp = np.zeros(self.L)
            inds = np.arange( self.all_inds[self.N-1]["a"],self.all_inds[self.N-1]["b"] )            
            Ln = self.all_inds[self.N-1]["win_len"]
            gn = np.roll( sg.tukey( Ln*2 ) , Ln )[Ln:]
            z_tmp[inds] = gn
            plt.plot(z_tmp)


            plt.show()
            # plt.axvline(start)
            # plt.axvline(end)
            # plt.axvline(middle)
            # plt.show()







    def get_frame_operator(self):
        
        #CONSTRUCTING THE FRAME OPERATOR-----------------------------------------------
        self.frame_operator = np.zeros(self.L)

        #MATRIX FORM CASE:
        if self.matrix_form:
            #calculate the max window length:
            self.M = np.array( list( map( lambda x : x["win_len"] , self.all_inds ) ) ).max()


            #first window using Tukey
            nb_zeros_concat = self.M-self.all_inds[0]["win_len"]
            bnew = self.all_inds[0]["b"] + nb_zeros_concat
            inds = np.arange( self.all_inds[0]["a"],bnew )
            Ln = self.all_inds[0]["win_len"]
            gn = np.roll( sg.tukey( Ln*2 ) , Ln )[:Ln]
            gn = np.concatenate(( gn,np.zeros(nb_zeros_concat) ))
            self.frame_operator[ inds ] += (gn**2)

            #The remaining windows--------------------------------------------------------------------
            for n in range(1,self.N//2):
                nb_zeros_concat = self.M-self.all_inds[n]["win_len"]
                bnew = self.all_inds[n]["b"] + nb_zeros_concat
                inds = np.arange( self.all_inds[n]["a"],bnew )
                Ln = self.all_inds[n]["win_len"]
                gn = self.all_inds[n]["window"]( Ln )
                gn = np.concatenate(( gn,np.zeros(nb_zeros_concat) ))
                self.frame_operator[ inds ] += (gn**2)

            #After the self.N//2 window we update the a inds in order to avoid indices problems out of range
            for n in range(self.N//2,self.N-1):
                nb_zeros_concat = self.M-self.all_inds[n]["win_len"]
                anew = self.all_inds[n]["a"] - nb_zeros_concat                
                inds = np.arange( anew,self.all_inds[n]["b"] )
                Ln = self.all_inds[n]["win_len"]
                gn = self.all_inds[n]["window"]( Ln )
                gn = np.concatenate(( np.zeros(nb_zeros_concat),gn ))
                self.frame_operator[ inds ] += (gn**2)                

            #last window using Tukey
            nb_zeros_concat = self.M-self.all_inds[self.N-1]["win_len"]
            anew = self.all_inds[self.N-1]["a"] - nb_zeros_concat               
            inds = np.arange( anew,self.all_inds[self.N-1]["b"] )
            Ln = self.all_inds[self.N-1]["win_len"]
            gn = np.roll( sg.tukey( Ln*2 ) , Ln )[Ln:]
            gn = np.concatenate(( np.zeros(nb_zeros_concat) ,gn ))
            self.frame_operator[ inds ] += (gn**2)

        #IRREGULAR MATRIX CASE:
        else:
            
            #first window using Tukey
            inds = np.arange( self.all_inds[0]["a"],self.all_inds[0]["b"] )
            Ln = self.all_inds[0]["win_len"]
            gn = np.roll( sg.tukey( Ln*2 ) , Ln )[:Ln]
            self.frame_operator[ inds ] += (gn**2)

            #The remaining windows
            for n in range(1,self.N-1):
                inds = np.arange( self.all_inds[n]["a"],self.all_inds[n]["b"] )
                Ln = self.all_inds[n]["win_len"]
                gn = self.all_inds[n]["window"]( Ln )
                self.frame_operator[ inds ] += (gn**2)

            #last window using Tukey
            inds = np.arange( self.all_inds[self.N-1]["a"],self.all_inds[self.N-1]["b"] )
            Ln = self.all_inds[self.N-1]["win_len"]
            gn = np.roll( sg.tukey( Ln*2 ) , Ln )[Ln:]
            self.frame_operator[ inds ] += (gn**2)


              


    @timeis
    def forward(self,signal):

        c = []

        #MATRIX FORM CASE:
        if self.matrix_form:
            #first window using Tukey
            nb_zeros_concat = self.M-self.all_inds[0]["win_len"]
            bnew = self.all_inds[0]["b"] + nb_zeros_concat
            inds = np.arange( self.all_inds[0]["a"],bnew )            
            fft_len = self.all_inds[0]["win_len"]
            gn = np.roll( sg.tukey( fft_len*2 ) , fft_len )[:fft_len] 
            gn = np.concatenate(( gn,np.zeros(nb_zeros_concat) ))                       
            c.append( rfft( signal[inds]*gn , norm="ortho" ) )            
                        
            #The remaining windows----------------------------------------------------------------------------------------
            for n in range(1,self.N//2):
                nb_zeros_concat = self.M-self.all_inds[n]["win_len"]
                bnew = self.all_inds[n]["b"] + nb_zeros_concat
                inds = np.arange( self.all_inds[n]["a"],bnew )
                fft_len = self.all_inds[n]["win_len"]
                gn = self.all_inds[n]["window"](fft_len)
                gn = np.concatenate(( gn,np.zeros(nb_zeros_concat) ))
                c.append( rfft( signal[inds]*gn , norm="ortho" ) )

            #After the self.N//2 window we update the a inds in order to avoid indices problems out of range
            for n in range(self.N//2,self.N-1):
                nb_zeros_concat = self.M-self.all_inds[n]["win_len"]
                anew = self.all_inds[n]["a"] - nb_zeros_concat                
                inds = np.arange( anew,self.all_inds[n]["b"] ) 
                fft_len = self.all_inds[n]["win_len"]
                gn = self.all_inds[n]["window"](fft_len)
                gn = np.concatenate(( np.zeros(nb_zeros_concat),gn ))
                c.append( rfft( signal[inds]*gn , norm="ortho" ) )                               

            
            #last window using Tukey
            nb_zeros_concat = self.M-self.all_inds[self.N-1]["win_len"]
            anew = self.all_inds[self.N-1]["a"] - nb_zeros_concat               
            inds = np.arange( anew,self.all_inds[self.N-1]["b"] )
            fft_len = self.all_inds[self.N-1]["win_len"]
            gn = np.roll( sg.tukey( fft_len*2 ) , fft_len )[fft_len:]    
            gn = np.concatenate(( np.zeros(nb_zeros_concat) ,gn ))
            c.append( rfft( signal[inds]*gn , norm="ortho" ) )                      

        #IRREGULAR MATRIX CASE:
        else:
            
            #first window using Tukey
            inds = np.arange( self.all_inds[0]["a"],self.all_inds[0]["b"] )
            fft_len = self.all_inds[0]["win_len"]
            gn = np.roll( sg.tukey( fft_len*2 ) , fft_len )[:fft_len]            
            c.append( rfft( signal[inds]*gn , norm="ortho" ) )            
                        
            #The remaining windows
            for n in range(1,self.N-1):
                fft_len = self.all_inds[n]["win_len"]
                inds = np.arange(self.all_inds[n]["a"],self.all_inds[n]["b"])
                gn = self.all_inds[n]["window"](fft_len)
                c.append( rfft( signal[inds]*gn , norm="ortho" ) )

            
            #last window using Tukey
            inds = np.arange( self.all_inds[self.N-1]["a"],self.all_inds[self.N-1]["b"] )
            fft_len = self.all_inds[self.N-1]["win_len"]
            gn = np.roll( sg.tukey( fft_len*2 ) , fft_len )[fft_len:]            
            c.append( rfft( signal[inds]*gn , norm="ortho" ) )                

        
        return c


    @timeis
    def backward(self,c):
        
        f_rec = np.zeros(self.L)

        if self.matrix_form:

            #first window using Tukey
            nb_zeros_concat = self.M-self.all_inds[0]["win_len"]
            bnew = self.all_inds[0]["b"] + nb_zeros_concat
            inds = np.arange( self.all_inds[0]["a"],bnew )    
            fft_len = self.all_inds[0]["win_len"]
            fn = np.real( irfft( c[0] , norm="ortho" ) )
            gn_dual = np.roll( sg.tukey( fft_len*2 ) , fft_len )[:fft_len]  
            gn_dual = np.concatenate(( gn_dual,np.zeros(nb_zeros_concat) ))/self.frame_operator[inds]        
            f_rec[inds] += fn*gn_dual                 

            for n in range(1,self.N//2):
                nb_zeros_concat = self.M-self.all_inds[n]["win_len"]
                bnew = self.all_inds[n]["b"] + nb_zeros_concat
                inds = np.arange( self.all_inds[n]["a"],bnew )                
                fft_len = self.all_inds[n]["win_len"]
                fn = np.real( irfft( c[n] , norm="ortho" ) )
                gn_dual = self.all_inds[n]["window"](fft_len)
                gn_dual = np.concatenate(( gn_dual,np.zeros(nb_zeros_concat) ))/self.frame_operator[inds]      
                f_rec[inds] += fn*gn_dual    

            #After the self.N//2 window we update the a inds in order to avoid indices problems out of range
            for n in range(self.N//2,self.N-1):
                nb_zeros_concat = self.M-self.all_inds[n]["win_len"]
                anew = self.all_inds[n]["a"] - nb_zeros_concat                
                inds = np.arange( anew,self.all_inds[n]["b"] )     
                fft_len = self.all_inds[n]["win_len"]
                fn = np.real( irfft( c[n] , norm="ortho" ) )
                gn_dual = self.all_inds[n]["window"](fft_len)
                gn_dual = np.concatenate(( np.zeros(nb_zeros_concat),gn_dual ))/self.frame_operator[inds]      
                f_rec[inds] += fn*gn_dual                                
             
            #last window using Tukey
            nb_zeros_concat = self.M-self.all_inds[self.N-1]["win_len"]
            anew = self.all_inds[self.N-1]["a"] - nb_zeros_concat               
            inds = np.arange( anew,self.all_inds[self.N-1]["b"] )            
            fft_len = self.all_inds[self.N-1]["win_len"]
            fn = np.real( irfft( c[self.N-1] , norm="ortho" ) )
            gn_dual = np.roll( sg.tukey( fft_len*2 ) , fft_len )[fft_len:]
            gn_dual = np.concatenate(( np.zeros(nb_zeros_concat),gn_dual ))/self.frame_operator[inds]                  
            f_rec[inds] += fn*gn_dual     
            
        else:
            #self.get_frame_operator()

            #first window using Tukey
            inds = np.arange( self.all_inds[0]["a"],self.all_inds[0]["b"] )
            fft_len = self.all_inds[0]["win_len"]
            fn = np.real( irfft( c[0] , norm="ortho" ) )
            gn_dual = np.roll( sg.tukey( fft_len*2 ) , fft_len )[:fft_len]/self.frame_operator[inds]  
            f_rec[inds] += fn*gn_dual                 

            for n in range(1,self.N-1):
                fft_len = self.all_inds[n]["win_len"]
                inds = np.arange(self.all_inds[n]["a"],self.all_inds[n]["b"])
                fn = np.real( irfft( c[n] , norm="ortho" ) )
                gn_dual = self.all_inds[n]["window"](fft_len)/self.frame_operator[inds]
                f_rec[inds] += fn*gn_dual    
             
            #last window using Tukey
            inds = np.arange( self.all_inds[self.N-1]["a"],self.all_inds[self.N-1]["b"] )
            fft_len = self.all_inds[self.N-1]["win_len"]
            fn = np.real( irfft( c[self.N-1] , norm="ortho" ) )
            gn_dual = np.roll( sg.tukey( fft_len*2 ) , fft_len )[fft_len:]/self.frame_operator[inds]  
            f_rec[inds] += fn*gn_dual     


        return f_rec




if __name__ =='__main__':

    def plot_NSGT(c):

        from scipy import interpolate
        c_matrix = []
        max_win_len = np.array( list( map( lambda x : len(x) , c ) ) ).max()
        for n in range(len(c)):
            N = len(c[n])
            fk = np.arange(N)*(22050/N)
            (x,y) = (fk,np.abs(c[n]))

            f = interpolate.interp1d(x, y)

            xnew = np.linspace(0, fk[N-1], max_win_len)
            ynew = f(xnew)
            c_matrix.append( ynew )  


        grid = np.array(c_matrix).T
        np.log10(grid, out=grid)
        grid *= 20
        pmax = np.percentile(grid, 99.99)
        plt.imshow(grid, aspect='auto', origin='lower', vmin=pmax-80, vmax=pmax,extent=[0,200,0,22050])

        plt.ylim(bottom=100)

        plt.yscale("log")

        loc = np.array([  100.,  1000., 10000.,22050.])
        labels = [ plt.Text(100.0, 0, '$\\mathdefault{100}$') , plt.Text(1000.0, 0, '$\\mathdefault{1000}$') , plt.Text(10000.0, 0, '$\\mathdefault{10000}$'), plt.Text(22050.0, 0, '$\\mathdefault{22050}$')  ]
        plt.yticks(loc,labels)    

        plt.ylim(top=22050)


        plt.colorbar()




    def timeis(func):
        '''Decorator that reports the execution time.'''

        def wrap(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            
            print(func.__name__, end-start)
            return result
        return wrap

    def cputime():
        utime, stime, cutime, cstime, elapsed_time = os.times()
        return utime    



    #x,s = load_music()
    x,s = librosa.load( '/home/nnanos/Downloads/glockenspiel.wav',sr=44100 )
    # x,s = librosa.load( '/home/nnanos/Downloads/hancock.wav',sr=44100 )
    # x = x[:44100*6]    

    # x1,s = librosa.load( "/home/nnanos/Desktop/sounds/C4.wav",sr=44100)
    # x2,s = librosa.load( "/home/nnanos/Desktop/sounds/Snare 1.wav",sr=44100)
    # x2 = np.concatenate((x2,np.zeros(len(x1)-len(x2))))
    # x2 = np.roll(periodic_extension(x2,2,"Rectangular",44100),44100)
    # x1 = periodic_extension(x1,2,"Rectangular",44100)
    #x = x1+x2

    #params
    min_scl = 512
    multiproc = True
    nb_processes = 6
    ovrlp_fact = 0.5

    #middle_window = sg.tukey
    middle_window = np.hanning
    matrix_form = False


    t1 = cputime()
    onsets = librosa.onset.onset_detect(y=x, sr=s, units="samples")
    scale_frame_obj = scale_frame(ksi_s=s,min_scl=min_scl,overlap_factor=ovrlp_fact,onset_seq=onsets,middle_window=middle_window,L=len(x),matrix_form=matrix_form,multiproc=multiproc)
        
    c = scale_frame_obj.forward(x)
    x_rec = scale_frame_obj.backward(c)
    t2 = cputime()

    norm = lambda x: np.sqrt(np.sum(np.abs(np.square(x))))
    rec_err = norm(x_rec - x)/norm(x)
    print("Reconstruction error : %.16e \t  \n  " %(rec_err) )
    print("Calculation time (forward and backward): %.3fs"%(t2-t1))


    plot_NSGT(c)

    # scale_frame_obj.plot_windows()
    # plt.plot(x_rec*(1/x_rec.max()))
    # plt.show()

    if not(matrix_form): 
        l = np.array( list( map( lambda x : len(x) , c ) )).sum()
    else:
        l = np.prod(np.array(c).shape)

    red = l/len(x)
    print("Redunduncy of the transform: %.3f"%(red))

    a = 0




