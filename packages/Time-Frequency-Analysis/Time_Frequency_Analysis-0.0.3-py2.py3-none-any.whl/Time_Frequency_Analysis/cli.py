"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mTime_Frequency_Analysis` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``Time_Frequency_Analysis.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``Time_Frequency_Analysis.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import argparse
import yaml

import librosa
from Audio_proc_lib.audio_proc_functions import * 
from Plotting_funcs.Plotting_util_and_other import *
import NSGT_CQT,STFT_custom,SCALE_FRAMES
import os
import scipy.signal as sg


parser = argparse.ArgumentParser(description='Command description.')
# parser.add_argument('names', metavar='NAME', nargs=argparse.ZERO_OR_MORE,
#                     help="A name of something.")

parser.add_argument('--front_end', type=str, default="STFT",
                        help='provide Transform name')

parser.add_argument('-p', '--params', type=yaml.load,
                        help='provide Transform parameters as a quoted json sting')

parser.add_argument('--plot_spectrograms', type=str, default="True",
                        help='flag for ploting the spectrograms')

args, _ = parser.parse_known_args()


def plot_transform(c,transform,matrix_form,sr,redunduncy):


    if transform=="NSGT_SCALE_FRAMES":

      if not(matrix_form):
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

        top_hz = sr//2
        top_time = (np.array( list( map( lambda x : len(x) , c ) )).sum()/redunduncy)*(1/sr)
        plt.imshow(grid, cmap="inferno" ,aspect='auto', origin='lower', vmin=pmax-80, vmax=pmax,extent=[0,top_time,0,top_hz])


        plt.ylim(bottom=100)

        plt.yscale("log")

        loc = np.array([  100.,  1000., 10000.,top_hz])
        labels = [ plt.Text(100.0, 0, '$\\mathdefault{100}$') , plt.Text(1000.0, 0, '$\\mathdefault{1000}$') , plt.Text(10000.0, 0, '$\\mathdefault{10000}$'), plt.Text(top_hz, 0, str(top_hz) )  ]
        plt.yticks(loc,labels)    

        plt.ylim(top=top_hz)



        plt.colorbar()
        plt.ylabel("Hz (log scale)")
        plt.xlabel("time (sec)")

        #plt.show()

      else:
        plot_spectrogram(np.array(c).T,44100,"log")



    if transform=="NSGT_CQT":

      if not(matrix_form):
        # top_time = (np.array( list( map( lambda x : len(x) , c ) )).sum())/redunduncy*(1/sr)*2
        #plot_cqt(f,c)
        from scipy import interpolate
        c_matrix = []
        max_win_len = np.array( list( map( lambda x : len(x) , c ) ) ).max()
        for k in range(len(c)):
            Nk = len(c[k])
            tk = np.arange(Nk)*(Nk/sr)
            (x,y) = (tk,np.abs(c[k]))

            f = interpolate.interp1d(x, y)

            xnew = np.linspace(0, tk[Nk-1], max_win_len)
            ynew = f(xnew)
            c_matrix.append( ynew )      

        grid = np.array(c_matrix)
        np.log10(grid, out=grid)
        grid *= 20
        pmax = np.percentile(grid, 99.99)

        top_hz = sr//2
        top_time = (np.array( list( map( lambda x : len(x) , c ) )).sum()/redunduncy)*(1/sr)*2
        plt.imshow(grid, cmap="inferno" ,aspect='auto', origin='lower', vmin=pmax-80, vmax=pmax,extent=[0,top_time,0,top_hz])

        plt.ylim(bottom=100)


        loc = np.array([  100.,  1000., 10000.,top_hz])
        labels = [ plt.Text(100.0, 0, '$\\mathdefault{100}$') , plt.Text(1000.0, 0, '$\\mathdefault{1000}$') , plt.Text(10000.0, 0, '$\\mathdefault{10000}$'), plt.Text(top_hz, 0, str(top_hz) )  ]
        plt.yticks(loc,labels)    

        plt.ylim(top=top_hz)


        plt.colorbar()
        plt.ylabel("Hz (linear scale)")
        plt.xlabel("time (sec)")

              
      else:
        plot_spectrogram(c,44100,"cqt_note")
        #pass

    if transform=="STFT":
      # librosa.display.specshow(librosa.amplitude_to_db(np.abs(c), ref=np.max),
      #               sr=sr, x_axis='time', y_axis="log")
      #grid = librosa.amplitude_to_db(np.abs(c), ref=np.max)
      grid = np.abs(c)
      grid = np.log10(np.abs(c), out=grid)
      grid *= 20
      pmax = np.percentile(grid, 99.99)
      plt.imshow(grid, cmap="inferno" ,aspect='auto', origin='lower', vmin=pmax-80, vmax=pmax,extent=[0,(1/sr)*c.shape[0]*2*c.shape[1]/redunduncy,0,sr//2])      
      plt.ylim(bottom=100)

      plt.yscale("log")

      loc = np.array([  100.,  1000., 10000.,22050.])
      labels = [ plt.Text(100.0, 0, '$\\mathdefault{100}$') , plt.Text(1000.0, 0, '$\\mathdefault{1000}$') , plt.Text(10000.0, 0, '$\\mathdefault{10000}$'), plt.Text(22050.0, 0, '$\\mathdefault{22050}$')  ]
      plt.yticks(loc,labels)    

      plt.ylim(top=22050)      
      
      plt.colorbar(format='%+2.0f dB')

      plt.ylabel("Frequnecy (Hz)")
      plt.xlabel("time (sec)")

      plt.tight_layout()



def main():    

    #load music
    x,s = load_music()
    # x = np.ones(262144)
    # s = 44100


    def cputime():
        utime, stime, cutime, cstime, elapsed_time = os.times()
        return utime


    def timeis(func):
        '''Decorator that reports the execution time.'''
  
        def wrap(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            
            print(func.__name__, end-start)
            return result
        return wrap


    if args.front_end=="NSGT_CQT":
        #NSGT cqt
        # ksi_min = 32.7
        # ksi_max = 5000
        # real=1
        # #ksi_max = 21049
        # B=12
        ksi_s = s
        #ksi_max =ksi_s//2-1
        # matrix_form = True


        #f = x[:len(x)-1]
        f=x
        L = len(f)

        t1 = cputime()
        nsgt = NSGT_CQT.NSGT_cqt(ksi_s=args.params["ksi_s"],ksi_min=args.params["ksi_min"],ksi_max=args.params["ksi_max"],B=args.params["B"],L = L,matrix_form=args.params["matrix_form"])
        
        c = nsgt.forward(f)
        f_rec = nsgt.backward(c)
        t2 = cputime()

        norm = lambda x: np.sqrt(np.sum(np.abs(np.square(x))))
        rec_err = norm(f_rec - f)/norm(f)
        print("LOG for the NSGT_CQT module (mine implementation https://github.com/nnanos/Time_Frequency_Analysis.git)-----------------------\n\n")
        print("Reconstruction relative error : %.16e \t  \n  " %(rec_err) )
        print("Calculation time (forward and backward): %.3fs"%(t2-t1))
        if not(args.params["matrix_form"]): 
            l = np.array( list( map( lambda x : len(x) , c ) )).sum()
        else:
            l = np.prod(c.shape)
        red = l/len(x)
        print("Redunduncy of the transform: %.3f\n\n\n"%(2*red))        

        #----------------------------------------------------------------------------------------

        #compare with library:
        t1 = cputime()
        nsgt = instantiate_NSGT( f , ksi_s , 'log',args.params["ksi_min"],args.params["ksi_max"],args.params["B"]*7,reducedform=0,matrixform=args.params["matrix_form"],multithreading=False)
        c1 = NSGT_forword(f,nsgt,pyramid_lvl=0,wavelet_type='db2')
        f_rec1 = NSGT_backward(c1,nsgt,pyramid_lvl=0,wavelet_type='db2')
        rec_err = norm(f_rec1 - f)/norm(f)
        t2 = cputime()

        print("LOG for the nsgt library (implemented by Thomas grrr https://github.com/grrrr/nsgt.git)-----------------------\n\n")
        print("Reconstruction relative error : %.16e \t  \n  " %(rec_err) )
        print("Calculation time (forward and backward): %.3fs"%(t2-t1)) 

        if not(args.params["matrix_form"]): 
            l = np.array( list( map( lambda x : len(x) , c1 ) )).sum()
        else:
            l = np.prod(c1.shape)
        red1 = l/len(x)
        print("Redunduncy of the transform: %.3f"%(red1))


        #_--------------------------------------------------------------------------------------------




        if args.plot_spectrograms=="True":
          plot_transform(c,transform=args.front_end,sr=args.params["ksi_s"],matrix_form=args.params["matrix_form"],redunduncy=2*red)
          plt.title("NSGT_cqt_mine")
          plt.figure()
          plot_transform(c1,transform=args.front_end,sr=args.params["ksi_s"],matrix_form=args.params["matrix_form"],redunduncy=red1)

          plt.title("NSGT_grr")  
          plt.show()

        #_--------------------------------------------------------------------------------------------


    elif args.front_end=="NSGT_SCALE_FRAMES":     
      # #params
      # min_scl = 128
      # multiproc = True
      # nb_processes = 6
      # ovrlp_fact = 1/10
      # #middle_window = sg.tukey
      # middle_window = np.hanning  

      lookup = {
        "np.hanning" : np.hanning,
        "sg.tukey" : sg.tukey
      } 

      middle_window = lookup[ args.params["middle_window"] ]

      t1 = cputime()
      if args.params["onset_det"]=="custom":

        #Onset det custom using hpss to estimate the drums:
        D = librosa.stft(x)
        H, P = librosa.decompose.hpss(D, margin=(1.0,7.0))
        y_perc = librosa.istft(P)
        onsets = librosa.onset.onset_detect(y=y_perc, sr=args.params["ksi_s"], units="samples")

      else:
        onsets = librosa.onset.onset_detect(y=x, sr=args.params["ksi_s"], units="samples")
      

      scale_frame_obj = SCALE_FRAMES.scale_frame(ksi_s=args.params["ksi_s"],min_scl=args.params["min_scl"],overlap_factor=args.params["ovrlp_fact"],onset_seq=onsets,middle_window=middle_window,L=len(x),matrix_form=args.params["matrix_form"],multiproc=args.params["multiproc"])
          
      c = scale_frame_obj.forward(x)
      x_rec = scale_frame_obj.backward(c)
      t2 = cputime()

      norm = lambda x: np.sqrt(np.sum(np.abs(np.square(x))))
      rec_err = norm(x_rec - x)/norm(x)
      print("LOG for the SCALE_FRAMES module (mine implementation https://github.com/nnanos/Time_Frequency_Analysis.git)-----------------------\n\n")      
      print("Reconstruction relative error : %.16e \t  \n  " %(rec_err) )
      print("Calculation time (forward and backward procedures): %.3fs"%(t2-t1))    
      if not(args.params["matrix_form"]): 
          l = np.array( list( map( lambda x : len(x) , c ) )).sum()
      else:
          l = np.prod(np.array(c).shape)
      red = l/len(x)
      print("Redunduncy of the transform: %.3f"%(2*red))        

      if args.plot_spectrograms=="True":
        plot_transform(c,transform=args.front_end,sr=s,matrix_form=args.params["matrix_form"],redunduncy=red)

        plt.title("Scale_frames_custom")      
        plt.show()


    elif args.front_end=="STFT":
        #TESTING STFT_custom----------------------------------------------
        # a = 512
        # M = 4096
        # support = 4096
        g = np.hanning(args.params["support"]) 
        x = np.concatenate((x,[0]))
        L = len(x)      


        t1 = cputime()
        stft = STFT_custom.STFT_CUSTOM(g,args.params["a"],args.params["M"],args.params["support"],L)
        X = stft.forward(x)
        x_rec = stft.backward(X)
        t2 = cputime()
        norm = lambda x: np.sqrt(np.sum(np.abs(np.square(x))))
        rec_err = norm(x_rec - x)/norm(x)
        print("LOG for the STFT_custom module (mine implementation https://github.com/nnanos/Time_Frequency_Analysis.git)-----------------------\n\n")
        print("Calculation time (forward and backward procedures): %.3fs"%(t2-t1))
        print("Reconstruction relative error : %.16e \t  \n  " %(rec_err) )  
        l = np.prod(X.shape)
        red = l/len(x)
        print("Redunduncy of the transform: %.3f"%(2*red))          

        #-----------------------------------------------------------------------------------------------

        #compare with library:
        t1 = cputime()
        X1 = librosa.stft(x,  n_fft =args.params["M"] , hop_length=args.params["a"], win_length=args.params["support"], window=g )
        x_rec1 = librosa.istft(X1,  hop_length=args.params["a"], win_length=args.params["support"], window=g )
        t2 = cputime()
        rec_err = norm(x_rec1 - x[:len(x_rec1)] )/norm(x[:len(x_rec1)])
        print("LOG for the stft function of librosa ( http://librosa.org/doc/main/generated/librosa.stft.html )-----------------------\n\n")
        print("Calculation time (forward and backward procedures): %.3fs"%(t2-t1))
        print("Reconstruction relative error : %.16e \t  \n  " %(rec_err) )  
        #-----------------------------------------------------------------------------------------------------------------------------------

        l = np.prod(X1.shape)
        red1 = l/len(x)
        print("Redunduncy of the transform: %.3f"%(2*red))        


        if args.plot_spectrograms=="True":
          plot_transform(X,transform=args.front_end,sr=s,matrix_form=1,redunduncy=2*red)
          plt.title("STFT_custom")

          plt.figure()
          plot_transform(X1,transform=args.front_end,sr=s,matrix_form=1,redunduncy=2*red1)

          plt.title("STFT_librsoa")
          plt.show()

        #------------------------------------------------------------------
