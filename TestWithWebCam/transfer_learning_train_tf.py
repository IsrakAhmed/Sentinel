import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_addons as tfa
import os
from tensorflow.keras import layers, models

# Dataset path
DATASET_PATH = "multi_class__short_ds_resized_128"
IMG_SIZE = (128, 128)
SEQUENCE_LENGTH = 10
BATCH_SIZE = 4
EPOCHS = 20
NUM_CLASSES = 4  # accident, fighting, fire, normal_resized

# Data augmentation
train_augmentation = tf.keras.Sequential([
    layers.TimeDistributed(layers.RandomFlip("horizontal")),
    layers.TimeDistributed(layers.RandomRotation(0.1)),
    layers.TimeDistributed(layers.RandomZoom(0.1)),
])

# Load video dataset (each class in its own folder, each video as frames in a subfolder)
def load_video_paths_and_labels(dataset_path):
    class_names = sorted(os.listdir(dataset_path))
    video_paths, labels = [], []
    for label, class_name in enumerate(class_names):
        class_dir = os.path.join(dataset_path, class_name)
        for video_folder in os.listdir(class_dir):
            video_path = os.path.join(class_dir, video_folder)
            if os.path.isdir(video_path):
                video_paths.append(video_path)
                labels.append(label)
    return video_paths, labels, class_names

def load_video_frames(video_path, img_size=IMG_SIZE, seq_len=SEQUENCE_LENGTH):
    frame_files = sorted([f for f in os.listdir(video_path) if f.endswith('.jpg') or f.endswith('.png')])
    frames = []
    for f in frame_files[:seq_len]:
        img = tf.keras.utils.load_img(os.path.join(video_path, f), target_size=img_size)
        img = tf.keras.utils.img_to_array(img) / 255.0
        frames.append(img)
    # Pad if not enough frames
    while len(frames) < seq_len:
        frames.append(tf.zeros((*img_size, 3)))
    return tf.stack(frames)

def video_generator(video_paths, labels, batch_size=BATCH_SIZE, augment=False):
    idx = 0
    while True:
        batch_videos, batch_labels = [], []
        for _ in range(batch_size):
            if idx >= len(video_paths):
                idx = 0
            video = load_video_frames(video_paths[idx])
            if augment:
                video = train_augmentation(tf.expand_dims(video, 0))[0]
            batch_videos.append(video)
            batch_labels.append(labels[idx])
            idx += 1
        yield tf.stack(batch_videos), tf.one_hot(batch_labels, NUM_CLASSES)

# Load data
video_paths, labels, class_names = load_video_paths_and_labels(DATASET_PATH)
num_samples = len(video_paths)
train_size = int(0.8 * num_samples)
train_videos, train_labels = video_paths[:train_size], labels[:train_size]
val_videos, val_labels = video_paths[train_size:], labels[train_size:]

train_gen = video_generator(train_videos, train_labels, augment=True)
val_gen = video_generator(val_videos, val_labels, augment=False)
steps_per_epoch = len(train_videos) // BATCH_SIZE
validation_steps = len(val_videos) // BATCH_SIZE

# Load a pretrained I3D model from TensorFlow Hub
base_model = hub.KerasLayer("https://tfhub.dev/deepmind/i3d-kinetics-400/1", trainable=False)

inputs = layers.Input(shape=(SEQUENCE_LENGTH, *IMG_SIZE, 3))
x = base_model(inputs)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)
model = models.Model(inputs, outputs)

# Freeze all but last Dense layers
for layer in model.layers[:-3]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy', tfa.metrics.F1Score(num_classes=NUM_CLASSES, average='macro')]
)

model.summary()

# Train
model.fit(
    train_gen,
    epochs=EPOCHS,
    steps_per_epoch=steps_per_epoch,
    validation_data=val_gen,
    validation_steps=validation_steps
)

# Optionally unfreeze more layers and fine-tune
# for layer in model.layers:
#     layer.trainable = True
# model.compile(...)
# model.fit(...)

model.save('finetuned_i3d_model.keras')
print('Training complete. Model saved as finetuned_i3d_model.keras')
