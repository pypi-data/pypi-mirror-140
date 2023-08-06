def image_reader(target_folder, target_class):
   #Setup a target directory for images
   img_folder = target_folder + '/'+ target_class 

   #Randomly sample target directory sub category and select a file
   random_file = random.sample(os.listdir(img_folder), 1)
   #Read the image and plot it using matplotlib
   img = mpimg.imread(img_folder + '/' + random_file[0])
   plt.imshow(img)
   plt.title(target_class)
   plt.axis('off');

   print(f'The shape of the image is {img.shape}')
   return random_file


def plot_generator(history_id, plot_size):
  """
  Outputs loss, accuracy, validation_loss and val_accuracy of a provided model and training curves

  """
  epochs = range(len(history_id.history['loss']))
  fitting__history = pd.DataFrame(history_id.history)

  #grabbing and plotting data for losses.
  plt.figure(figsize = (plot_size))
  loss = fitting__history[['loss', 'val_loss']]
  plt.plot(loss)
  plt.title('training loss curves')
  plt.xlabel(epochs)
  plt.legend(loss)

  #grabbing and plotting data for accuracy.
  plt.figure(figsize = (plot_size))
  accuracy = fitting__history[['accuracy', 'val_accuracy']]
  plt.plot(accuracy)
  plt.title('training accuracy curves')
  plt.xlabel(epochs)
  plt.legend(accuracy);


def load_custom_images(custom_path, model, class_names, class_mode):
  #rescaling and normalizing custom images
  custom_gen = ImageDataGenerator(rescale = 1/255.)
  image_generator = custom_gen.flow_from_directory(custom_path,
                                                    target_size = (224, 224),
                                                    batch_size = 32,
                                                    class_mode = class_mode)
  #Making prediction on our normalized custom image
  model_prediction = model.predict(image_generator)

  #multiclass classification.
  if len(model_prediction[0]) > 1:
    model_prediction.argmax()

    print(model_prediction)
  else:
    model_prediction.round()
  
  #Extentiating classes
  custom_image, custom_label = image_generator.next()
  
  #Viewing images and predictions from our model
  plt.figure(figsize = (10, 8))
  for i in range(4):
    ax = plt.subplot(2, 2, i+1)
    random_index = random.choice(range(len(custom_image)))

    #using color code to different predictions.
    if model_prediction[random_index] == custom_label[random_index]:
      color = 'green'
    else:
      color = 'red'
    #Extentiating predicted valued and actual values.
    actual_label =(custom_label[random_index])
    actual_label = class_names[int(actual_label)]

    pred_label = (model_prediction[random_index])
    pred_label = class_names[int(pred_label)]

    plt.imshow(custom_image[random_index])

    
    plt.title("pred:{} (Actual: {})".format(pred_label,
                                            actual_label),
                                              color=color)
    plt.axis(False);





# Our function needs a different name to sklearn's plot_confusion_matrix
def make_confusion_matrix(y_true, y_pred, classes=None, figsize=(10, 10), text_size=15):
    # Create the confustion matrix
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis] # normalize it
    n_classes = cm.shape[0] # find the number of classes we're dealing with

  # Plot the figure and make it pretty
    fig, ax = plt.subplots(figsize=figsize)
    cax = ax.matshow(cm, cmap=plt.cm.Blues) # colors will represent how 'correct' a class is, darker == better
    fig.colorbar(cax)

  # Are there a list of classes?
    if classes:
        labels = classes
    else:
        labels = np.arange(cm.shape[0])
  
  # Label the axes
    ax.set(title="Confusion Matrix",
         xlabel="Predicted label",
         ylabel="True label",
         xticks=np.arange(n_classes), # create enough axis slots for each class
         yticks=np.arange(n_classes), 
         xticklabels=labels, # axes will labeled with class names (if they exist) or ints
         yticklabels=labels)
  
  # Make x-axis labels appear on bottom
    ax.xaxis.set_label_position("bottom")
    ax.xaxis.tick_bottom()
    # Set the threshold for different colors
    threshold = (cm.max() + cm.min()) / 2.

  # Plot the text on each cell
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, f"{cm[i, j]} ({cm_norm[i, j]*100:.1f}%)",
             horizontalalignment="center",
             color="white" if cm[i, j] > threshold else "black",
             size=text_size)