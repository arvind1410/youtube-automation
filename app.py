from pathlib import Path

from src.audio import generate_voice_over
from src.config import cfg
from src.logger import logger
from src.openai_generation import run_openai_generation
from src.utils import (
    generate_video_meta,
    get_cookies,
    get_source_files,
    prep_directories,
    read_data_from_file,
    split_openai_output,
)
from src.video import get_audio, get_stock_videos, make_video
from src.video_processing import save_videos
from moviepy.editor import *
import os
import pyttsx3
import soundfile as sf
engine = pyttsx3.init()
cookies = get_cookies()


def run(file_path: Path):
    # read data from txt file
    input_data: str = read_data_from_file(file_path)
    logger.info("Input data loaded")
    # run openai prompt with file
    openai_output = ""
    for _ in range(3):
        cur_output = run_openai_generation(input_data, "prompt.txt")
        cur_output = cur_output.replace('"', "").replace("'", "")
        if len(cur_output.split()) > len(openai_output.split()):
            openai_output = cur_output
        if len(openai_output.split()) >= 500:
            break
    logger.info("OpenAI response received")
    logger.info(openai_output)
    # split data into pieces
    splitted_output = split_openai_output(openai_output)

    file_output_dir = r"{cfg.PROCESS_DIR}/{file_path.stem}"
    # save video metadata into folder
    generate_video_meta(splitted_output, file_output_dir)

    # generate audio
    # audio_duration = generate_voice_over(splitted_output, file_output_dir)

    audio_data = open("C:\\Users\\arvin\\Documents\\GitHub\\Open Source\\text2youtube\\{cfg.PROCESS_DIR}\\{file_path.stem}\\video_text.txt","r")

    engine.setProperty('rate', 175)  # setting up new voice rate

    """VOLUME"""
    engine.setProperty('volume', 1.0)  # setting up volume level  between 0 and 1

    """VOICE"""
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # changing index, changes voices. 1 for female

    """PITCH"""  # Print current pitch value
    engine.setProperty('pitch', 100)

    engine.say("Step into the world of ancient Egypt, where the pyramids of Giza stood tall as architectural marvels")
    engine.runAndWait()
    engine.stop()

    audio_data = audio_data.read()
    print(audio_data)

    logger.info(audio_data)
    engine.save_to_file(audio_data,'C:\\Users\\arvin\\Documents\\GitHub\\Open Source\\text2youtube\\{cfg.PROCESS_DIR}\\{file_path.stem}\\audio.mp3')
    engine.runAndWait()

    temp = sf.SoundFile("C:\\Users\\arvin\\Documents\\GitHub\\Open Source\\text2youtube\\{cfg.PROCESS_DIR}\\{file_path.stem}\\audio.mp3")
    temp.frames / temp.samplerate

    # save videos for further use
    save_videos(splitted_output, temp.frames / temp.samplerate, file_output_dir, cookies, cfg.YT_PROBA)

    directory = os.fsencode(
        "C:\\Users\\arvin\\Documents\\GitHub\\Open Source\\text2youtube\\{cfg.PROCESS_DIR}\\{file_path.stem}\\videos")

    clips = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        logger.info(filename)
        if filename.endswith(".mp4"):
            clips.append(VideoFileClip("C:\\Users\\arvin\\Documents\\GitHub\\Open Source\\text2youtube\\{cfg.PROCESS_DIR}\\{file_path.stem}\\videos\\"+filename))
        else:
            continue
    final = concatenate_videoclips(clips, method="compose")

    # writing the video into a file / saving the combined video
    final.write_videofile(
        "C:\\Users\\arvin\\Documents\\GitHub\\Open Source\\text2youtube\\{cfg.PROCESS_DIR}\\{file_path.stem}\\videos\\finalCut.mp4",
        codec="libx264", audio_codec="aac", fps=30)

    # generate video
    # make_video(
    #     splitted_output,
    #     get_audio(file_output_dir),
    #     get_stock_videos(f"{file_output_dir}/videos"),
    #     f"{OUTPUT_DIR}/{file_path.stem}.mp4",
    # )


def main():
    logger.info("App start")
    prep_directories()
    for file_path in get_source_files(cfg.SOURCE_DIR):
        logger.info(f"Processing: {file_path}")
        run_completed = False
        while not run_completed:
            # try:
            run(file_path)
            run_completed = True
            # except Exception as e:
            #     print("Failed on file ", file_path, " with exception ", e)


if __name__ == "__main__":
    main()
