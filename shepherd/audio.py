import simpleaudio as sa

wave_obj = sa.WaveObject.from_wave_file('static/onew.wav')
play_obj = wave_obj.play()
play_obj.wait_done()

# roll = sa.WaveObject.from_wave_file('sound.wav')
# playbacks = []
# def play_perk_music():
#     stop_music()
#     playback = roll.play()
#     playbacks.append(playback)
# def stop_music():
#     for playback in playbacks:
#         playback.stop()


# play_perk_music()
# time.sleep(2)
# stop_music()
# time.sleep(2)
# play_perk_music()
# time.sleep(2)
# stop_music()
# time.sleep(1000)