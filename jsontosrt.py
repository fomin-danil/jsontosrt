import streamlit as st
import json

# Function to convert words to SRT entries with correct timing
def words_to_srt(words):
    srt_entries = []
    sequence_number = 1
    current_line = []
    current_line_start_time = None
    current_line_end_time = None
    pause_threshold = 1.5  # Threshold for pause in seconds
    previous_end = 0

    for word in words:
        if "start" in word and "end" in word:
            text = word["word"]
            start_time = word["start"]
            end_time = word["end"]

            # Check for pause
            if start_time - previous_end >= pause_threshold:
                start_formatted = format_time(previous_end)
                end_formatted = format_time(start_time)
                # Russian text for "ПАУЗА"
                pause_text = "\u041F\u0410\u0423\u0417\u0410"
                pause_entry = f"{sequence_number}\n{start_formatted} --> {end_formatted}\n{pause_text}\n\n"
                srt_entries.append(pause_entry)
                sequence_number += 1

            # Initialize start time for the current line
            if current_line_start_time is None:
                current_line_start_time = start_time

            # Append current word to the line
            current_line.append(text)

            # Update end time for the current line
            current_line_end_time = end_time

            # Check for line end conditions (dot or comma)
            if text.endswith('.') or text.endswith(','):
                # Create SRT entry if the current line has more than one word
                if len(current_line) > 1:
                    srt_entry = f"{sequence_number}\n"
                    srt_entry += f"{format_time(current_line_start_time)} --> {format_time(current_line_end_time)}\n"
                    srt_entry += ' '.join(current_line) + '\n\n'

                    # Append entry to SRT list
                    srt_entries.append(srt_entry)

                    # Reset line and increment sequence number
                    current_line = []
                    current_line_start_time = None
                    current_line_end_time = None
                    sequence_number += 1

            previous_end = end_time

        else:
            # Handle words without explicit start and end times
            text = word["word"]

            # Append current word to the line
            current_line.append(text)

            # Check for line end conditions (dot or comma)
            if text.endswith('.') or text.endswith(','):
                # Create SRT entry if the current line has more than one word
                if len(current_line) > 1:
                    srt_entry = f"{sequence_number}\n"
                    srt_entry += f"{format_time(0)} --> {format_time(0)}\n"  # Use dummy timings
                    srt_entry += ' '.join(current_line) + '\n\n'

                    # Append entry to SRT list
                    srt_entries.append(srt_entry)

                    # Reset line and increment sequence number
                    current_line = []
                    sequence_number += 1

    return srt_entries

# Function to format time in SRT format (00:00:00,000)
def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

# Streamlit app
def main():
    st.title("Сконвертировать JSON в&nbsp;субтитры")

    # File uploader for JSON file
    uploaded_file = st.file_uploader("Перетащи или открой файл", type=["json"])

    if uploaded_file is not None:
        # Read data from uploaded JSON file
        data = json.load(uploaded_file)

        # Extract words data
        words_data = data["results"][0]["words"]

        # Convert words to SRT format
        srt_entries = words_to_srt(words_data)

        # Download SRT file
        st.markdown("### Скачать .srt")
        srt_file_name = "output.srt"
        srt_file_text = "\n".join(srt_entries)
        st.download_button(label="Скачать .srt", data=srt_file_text, file_name=srt_file_name, mime="text/plain")

        # Display SRT entries
        st.header("Текст субтитров")
        for entry in srt_entries:
            st.text(entry)

if __name__ == "__main__":
    main()