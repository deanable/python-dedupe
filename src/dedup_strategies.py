from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Union
import os
import time

from src.dedup_engine import DuplicateGroup

class KeepStrategy(Enum):
    LARGEST = "largest"
    OLDEST = "oldest"
    NEWEST = "newest"
    MANUAL = "manual"
    FIRST = "first"


@dataclass
class DedupDecision:
    keep_item: Optional[str]
    remove_items: List[str]
    reason: str


def get_file_metadata(file_path: str) -> Dict[str, Union[int, float]]:
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'mtime': stat.st_mtime
        }
    except Exception:
        # On error (e.g. file missing), return values that deprioritize the file
        # Size 0 (smallest), mtime current time (newest? or inf?)
        # For oldest strategy, we want this to be "very new" so it's not picked.
        # For newest strategy, we want this to be "very old" so it's not picked?
        # Actually, if file is missing, we shouldn't keep it.
        # But we can't easily know which strategy is calling this.
        # Let's return 0 size and current time for mtime.
        return {'size': 0, 'mtime': time.time()}


def apply_keep_first(group: DuplicateGroup) -> DedupDecision:
    if not group.items:
        return DedupDecision(keep_item=None, remove_items=[], reason="Empty group")

    keep = group.items[0]
    remove = group.items[1:]
    return DedupDecision(keep_item=keep, remove_items=remove, reason="Keep first item")


def apply_keep_largest(group: DuplicateGroup) -> DedupDecision:
    if not group.items:
        return DedupDecision(keep_item=None, remove_items=[], reason="Empty group")

    # Sort by size descending.
    # If sizes are equal, sort by path to be deterministic?
    # Python sort is stable, so original order is preserved for ties.
    # To be fully deterministic, we can sort by (size, path).
    # But path direction is arbitrary.
    # Let's just use size.
    sorted_items = sorted(group.items, key=lambda x: get_file_metadata(x)['size'], reverse=True)
    keep = sorted_items[0]
    remove = [item for item in group.items if item != keep]

    return DedupDecision(keep_item=keep, remove_items=remove, reason="Keep largest file")


def apply_keep_oldest(group: DuplicateGroup) -> DedupDecision:
    if not group.items:
        return DedupDecision(keep_item=None, remove_items=[], reason="Empty group")

    # Sort by mtime ascending (oldest first)
    sorted_items = sorted(group.items, key=lambda x: get_file_metadata(x)['mtime'])
    keep = sorted_items[0]
    remove = [item for item in group.items if item != keep]

    return DedupDecision(keep_item=keep, remove_items=remove, reason="Keep oldest file")


def apply_keep_newest(group: DuplicateGroup) -> DedupDecision:
    if not group.items:
        return DedupDecision(keep_item=None, remove_items=[], reason="Empty group")

    # Sort by mtime descending (newest first)
    sorted_items = sorted(group.items, key=lambda x: get_file_metadata(x)['mtime'], reverse=True)
    keep = sorted_items[0]
    remove = [item for item in group.items if item != keep]

    return DedupDecision(keep_item=keep, remove_items=remove, reason="Keep newest file")


def select_item_to_keep(group: DuplicateGroup, strategy: KeepStrategy) -> DedupDecision:
    if strategy == KeepStrategy.FIRST:
        return apply_keep_first(group)
    elif strategy == KeepStrategy.LARGEST:
        return apply_keep_largest(group)
    elif strategy == KeepStrategy.OLDEST:
        return apply_keep_oldest(group)
    elif strategy == KeepStrategy.NEWEST:
        return apply_keep_newest(group)
    elif strategy == KeepStrategy.MANUAL:
        # Manual strategy implies no automatic decision.
        # We return a decision with no keep_item, implying user must decide.
        return DedupDecision(keep_item=None, remove_items=[], reason="Manual review required")
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def generate_dedup_plan(groups: List[DuplicateGroup], strategy: KeepStrategy) -> List[DedupDecision]:
    """
    Generates a list of decisions for the given groups using the specified strategy.
    """
    decisions = []
    for group in groups:
        decision = select_item_to_keep(group, strategy)
        decisions.append(decision)
    return decisions
