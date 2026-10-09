
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 60, separator: str = "\n") -> list[str]:
    if not text:
        return []

    # Split into raw segments based on the separator
    segments = text.split(separator)

    chunks = []
    current_segments = []
    current_len = 0

    for segment in segments:
        segment_len = len(segment)

        # Calculate additional length needed if adding this segment
        # (account for separator length between existing segments)
        added_len = (
            segment_len
            if not current_segments
            else len(separator) + segment_len
        )

        if current_len + added_len <= chunk_size:
            current_segments.append(segment)
            current_len += added_len
        else:
            # Join and save the completed chunk
            if current_segments:
                chunk_str = separator.join(current_segments)
                chunks.append(chunk_str)

            # Handle overlap logic for the next chunk
            if overlap > 0 and current_segments:
                # Retain trailing portion within overlap limit
                overlap_text = chunk_str[-overlap:]
                current_segments = [overlap_text, segment]
                current_len = len(overlap_text) + len(separator) + segment_len
            else:
                current_segments = [segment]
                current_len = segment_len

    # Append any remaining segments
    if current_segments:
        chunks.append(separator.join(current_segments))

    return chunks

