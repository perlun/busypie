import asyncio
from contextlib import contextmanager
from threading import Thread
from time import sleep

import pytest
from busypie import (FIVE_HUNDRED_MILLISECONDS, MILLISECOND,
                     ConditionTimeoutError, reset_defaults,
                     set_default_timeout, wait)

from backports.asyncio import run


def test_wait_until_condition_passed():
    with assert_done_after(seconds=0.3) as c:
        wait().until(lambda: c.done)


def test_wait_until_condition_passed_after_using_event_loop():
    run(asyncio.sleep(0.1))
    with assert_done_after(seconds=0.3) as c:
        wait().until(lambda: c.done)


@contextmanager
def assert_done_after(seconds):
    sleeper = Sleeper()
    sleeper.sleep_for(seconds)
    yield sleeper
    assert sleeper.done


@pytest.mark.timeout(1)
def test_timeout_when_condition_did_not_meet_in_time():
    with pytest.raises(ConditionTimeoutError):
        wait().at_most(FIVE_HUNDRED_MILLISECONDS).until(lambda: 1 == 2)
    with pytest.raises(ConditionTimeoutError):
        wait().at_most(100, MILLISECOND).until(lambda: False)


def test_wait_until_condition_fail():
    with assert_done_after(seconds=0.2) as c:
        wait().during(lambda: not c.done)


@pytest.mark.timeout(0.6)
def test_set_default_timeout():
    set_default_timeout(500, MILLISECOND)
    with pytest.raises(ConditionTimeoutError):
        wait().until(lambda: 1 == 2)


def test_reset_default_timeout():
    set_default_timeout(200, MILLISECOND)
    reset_defaults()
    with assert_done_after(seconds=0.4) as c:
        wait().until(lambda: c.done)


def test_retrieve_condition_result():
    assert wait().until(lambda: 3) == 3


def test_nested_waits():
    def condition():
        return wait().until(lambda: True)

    assert wait().until(condition)


class Sleeper:
    done = False

    def sleep_for(self, start):
        Thread(target=self._wake_up_after, args=(start,)).start()

    def _wake_up_after(self, seconds):
        sleep(seconds)
        self.done = True
