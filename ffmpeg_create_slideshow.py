import os
import subprocess

def get_media_files(directory):
    supported_extensions = ('.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi')
    media_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(supported_extensions)]
    return sorted(media_files)

def generate_filter_complex(media_files, slide_duration, transition_duration, resolution, framerate, transition_effect):
    filter_complex = ""
    width, height = resolution.split('x')

    for i, media_file in enumerate(media_files):
        filter_complex += (
            f"[{i}:v]scale='if(gt(a,{width}/{height}),{width},-1)':'if(gt(a,{width}/{height}),-1,{height})',"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[f{i}];"
        )
    
    for i in range(len(media_files) - 1):
        offset = slide_duration * (i + 1) - transition_duration
        if transition_effect in ['fade', 'wipeleft', 'wipeup', 'wipedown', 'wiperight', 'slideleft', 'slideup', 'slidedown', 'slideright', 'smoothleft', 'smoothup', 'smoothdown', 'smoothright', 'circleopen', 'circleclose', 'radial', 'fadeblack', 'fadewhite', 'rectcrop', 'distance']:
            filter_complex += f"[f{i}][f{i+1}]xfade=transition={transition_effect}:duration={transition_duration}:offset={offset}[v{i+1}];"
        else:
            filter_complex += f"[f{i}][f{i+1}]xfade=duration={transition_duration}:offset={offset}[v{i+1}];"

    final_output = f"[v{len(media_files) - 1}]" if len(media_files) > 1 else f"[f0]"
    return filter_complex, final_output

def create_ffmpeg_command(media_files, slide_duration, transition_duration, resolution, framerate, output_file, encoding_preset, transition_effect):
    input_files = []
    filter_complex, final_output = generate_filter_complex(media_files, slide_duration, transition_duration, resolution, framerate, transition_effect)

    for media_file in media_files:
        if media_file.lower().endswith(('.jpg', '.jpeg')):
            input_files.extend(['-loop', '1', '-t', str(slide_duration), '-framerate', str(framerate), '-i', media_file])
        else:
            input_files.extend(['-t', str(slide_duration), '-framerate', str(framerate), '-i', media_file])
    
    ffmpeg_command = (
        ['ffmpeg', '-y'] + input_files +
        ['-filter_complex', filter_complex, '-map', final_output, '-t', str(len(media_files) * (slide_duration + transition_duration)), 
         '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', encoding_preset, output_file]
    )

    return ffmpeg_command

def main(directory, slide_duration=3, transition_duration=1, resolution='1280x720', framerate=30, output_file='slideshow.mp4', encoding_preset='fast', transition_effect='fade'):
    media_files = get_media_files(directory)
    if not media_files:
        print("No media files found in the specified directory.")
        return

    ffmpeg_command = create_ffmpeg_command(media_files, slide_duration, transition_duration, resolution, framerate, output_file, encoding_preset, transition_effect)
    subprocess.run(ffmpeg_command)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a slideshow with transitions.")
    parser.add_argument('directory', type=str, help="Directory containing media files")
    parser.add_argument('--slide_duration', type=int, default=3, help="Duration of each slide in seconds")
    parser.add_argument('--transition_duration', type=int, default=1, help="Duration of each transition in seconds")
    parser.add_argument('--resolution', type=str, default='1280x720', help="Output resolution, e.g., 1920x1080")
    parser.add_argument('--framerate', type=int, default=30, help="Frame rate of the output video")
    parser.add_argument('--output_file', type=str, default='slideshow.mp4', help="Name of the output video file")
    parser.add_argument('--encoding_preset', type=str, default='fast', help="x264 encoding preset, e.g., ultrafast, fast, medium, slow")
    parser.add_argument('--transition_effect', type=str, default='fade', help="Transition effect, e.g., fade, wipeleft, wipeup, wipedown, wiperight, slideleft, slideup, slidedown, slideright, smoothleft, smoothup, smoothdown, smoothright, circleopen, circleclose, radial, fadeblack, fadewhite, rectcrop, distance")
    args = parser.parse_args()
    main(args.directory, args.slide_duration, args.transition_duration, args.resolution, args.framerate, args.output_file, args.encoding_preset, args.transition_effect)
