# AI_Water
1) Run main.py, this will create all the need file directories.
2) Rename your dataset to dataset and extract it into your currnet working directory (Where main was ran). labels.json also needs to be placed to the same directory.
3) If you’re loading in weights rename the .h5 file to asf_cnn.h5 and move it to the working directory. If you’re not loading them in and you're restarting the training of the CNN, comment out the lines:

      with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
        classifier = load_model(os.path.join(CURRENT_DIRECTORY, 'asf_cnn.h5'))

And uncomment out the line:

    	# classifier.compile('adam', loss='binary_crossentropy', metrics=['accuracy'])

4) Run main.py again. 
