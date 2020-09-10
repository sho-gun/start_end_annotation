# start_end_annotation

## Usage
```
# Linux
python3 main.py -i YOUR_INPUT_DIRECTORY

# Windows
py main.py -i YOUR_INPUT_DIRECTORY
```

Input directory must have following structure.
```
input_dir_root/
    └ CLASS_DIR/
        └ VIDEO_DIR/
            └ frames/
                └ 0000.jpg
                └ 0001.jpg
                └ 0002.jpg
```

Example:
```
input_dir_root/
    └ straight_left_straight/
        ├ 20200910_0000/
        │   └ frames/
        │       └ 0000.jpg
        │       └ 0001.jpg
        └ 20200910_0001/
            └ frames/
                └ 0000.jpg
                └ 0001.jpg
                └ 0002.jpg
```
