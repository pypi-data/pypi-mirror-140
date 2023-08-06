"""
Entrypoint module, in case you use `python -mTime_Frequency_Analysis`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""
#from Time_Frequency_Analysis.cli import main
from cli import main


#execute the __main__.py module in order to test (and compare with the library) the transforms  
# 1)execution time 2)perfect reconstruction property 3)visualization   

#Examples for the cli to run:
#For NSGT_CQT : python __main__.py --front_end NSGT_CQT -p "{ ksi_s : 44100 , ksi_min : 32.07 , ksi_max : 3907.07 , B : 12 , matrix_form : 1 }" --plot_spectrograms True

#For NSGT_scale : NSGT_scale  python __main__.py --front_end NSGT_SCALE_FRAMES -p "{ onset_det : custom , ksi_s : 44100 , min_scl : 128 , ovrlp_fact : 0.5 , middle_window : np.hanning , matrix_form : 0 , multiproc : 1 }" --plot_spectrograms True

#For STFT : python __main__.py --front_end STFT -p "{ a : 1024 , M : 4096 , support : 4096 }" --plot_spectrograms True

if __name__ == "__main__":

    main()



