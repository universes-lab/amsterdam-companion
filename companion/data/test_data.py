import json
from pathlib import Path
from companion.data.event_reader import EventReader
from companion.data.memory_manager import MemoryManager

def run_test():
    events_file = Path('supervisor/events.jsonl')
    with open(events_file, 'w', encoding='utf-8') as f:
        f.write('{"type":"live_request","direction":"ru-nl","latency_ms":920}\n')

    reader = EventReader(events_file)
    events, offset = reader.read_new_events()
    print(f'Events read: {len(events)}')
    assert len(events) == 1

    stats = reader.aggregate_events(events)
    print(f'Aggregated: live_requests={stats["live_mode_requests"]}')

    mm = MemoryManager(Path('supervisor/memory.json'), Path('supervisor/archive'))
    mm.update(stats)
    print('Memory saved')
    print('✅ Все тесты пройдены')

if __name__ == "__main__":
    run_test()
