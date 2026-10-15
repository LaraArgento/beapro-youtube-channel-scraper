from botcity.web import WebBot, Browser, By
from botcity.maestro import (
    BotMaestroSDK,
    AutomationTaskFinishStatus,
    AlertType,
    Column,
    ErrorType,
)
from typing import Optional

from webdriver_manager.firefox import GeckoDriverManager
from config import get_env_credentials

LOG_LABEL = "YoutubeChannelLog"
DATAPOOL_LABEL = "YoutubeChannels"


def ensure_log(maestro: BotMaestroSDK):
    try:
        maestro.get_log(activity_label=LOG_LABEL)
        return
    except Exception:
        pass
    maestro.new_log(
        activity_label=LOG_LABEL,
        columns=[
            Column(name="Handle", label="handle", width=150),
            Column(name="Subscribers", label="subscribers", width=150),
            Column(name="Videos", label="videos", width=100),
        ],
    )


def collect_channel_info(bot: WebBot, channel_handle: str) -> Optional[dict]:
    url = f"https://www.youtube.com/@{channel_handle.lstrip('@')}"
    bot.navigate_to(url)
    bot.wait(3000)

    # Dismiss cookie popup if present
    try:
        accept_btn = bot.find_element(
            "button[aria-label*='Accept']", By.CSS_SELECTOR, waiting_time=3000
        )
        if accept_btn:
            accept_btn.click()
            bot.wait(1000)
    except Exception:
        pass

    # Verify channel exists
    try:
        bot.find_element("#channel-name", By.CSS_SELECTOR, waiting_time=8000)
    except Exception:
        return None

    bot.wait(1500)

    subscribers, videos = _parse_metadata(bot)

    return {
        "subscribers": subscribers,
        "videos": videos,
    }


def _parse_metadata(bot: WebBot) -> tuple:
    """Parse subscriber and video count from the channel metadata block."""
    try:
        el = bot.driver.find_element(By.CSS_SELECTOR, "yt-content-metadata-view-model")
        parts = [p.strip() for p in el.text.split("\n") if p.strip() and p.strip() != "•"]
        subscribers = parts[1] if len(parts) > 1 else "N/A"
        videos = parts[2] if len(parts) > 2 else "N/A"
        return subscribers, videos
    except Exception:
        return "N/A", "N/A"


def action(execution=None):
    login, key, server, task_id_env = get_env_credentials()

    BotMaestroSDK.VERIFY_SSL_CERT = False
    maestro = BotMaestroSDK.from_sys_args(
        default_server=server,
        default_login=login,
        default_key=key,
    )
    execution = maestro.get_execution(task_id=task_id_env)

    task_id = execution.task_id

    ensure_log(maestro)

    datapool = maestro.get_datapool(DATAPOOL_LABEL)

    if not datapool.has_next():
        print("[datapool] No pending items. Finishing task.")
        maestro.finish_task(
            task_id=task_id,
            status=AutomationTaskFinishStatus.SUCCESS,
            message="No pending items in the Datapool.",
            total_items=0,
            processed_items=0,
            failed_items=0,
        )
        return

    item = datapool.next(task_id=task_id)
    channel_handle = item["channel_handle"]
    print(f"[datapool] Consumed item: {channel_handle}")

    bot = WebBot()
    bot.browser = Browser.FIREFOX
    bot.driver_path = GeckoDriverManager().install()
    bot.start_browser()
    bot.set_screen_resolution(1280, 900)

    try:
        print(f"[browser] Navigating to: youtube.com/@{channel_handle.lstrip('@')}")
        info = collect_channel_info(bot, channel_handle)

        if info is None:
            screenshot_path = f"not_found_{channel_handle.lstrip('@')}.png"
            bot.screenshot(filepath=screenshot_path)
            maestro.post_artifact(
                task_id=task_id,
                artifact_name=screenshot_path,
                filepath=screenshot_path,
            )
            maestro.alert(
                task_id=task_id,
                title="Channel not found",
                message=f"Channel '{channel_handle}' was not found on YouTube.",
                alert_type=AlertType.WARN,
            )
            item.report_error(
                error_type=ErrorType.BUSINESS,
                finish_message=f"Channel '{channel_handle}' not found.",
            )
            print(f"[warn] Channel '{channel_handle}' not found.")
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.PARTIALLY_COMPLETED,
                message="Channel not found on YouTube.",
                total_items=1,
                processed_items=0,
                failed_items=1,
            )
            return

        print(f"[ok] {channel_handle} — {info['subscribers']} — {info['videos']}")

        maestro.new_log_entry(
            activity_label=LOG_LABEL,
            values={
                "handle": channel_handle,
                "subscribers": info["subscribers"],
                "videos": info["videos"],
            },
        )

        if info["subscribers"] == "N/A":
            maestro.alert(
                task_id=task_id,
                title="Subscriber count unavailable",
                message=f"Could not read subscriber count for '{channel_handle}'.",
                alert_type=AlertType.WARN,
            )

        screenshot_path = f"channel_{channel_handle.lstrip('@')}.png"
        bot.screenshot(filepath=screenshot_path)
        maestro.post_artifact(
            task_id=task_id,
            artifact_name=screenshot_path,
            filepath=screenshot_path,
        )

        item.report_done(finish_message=f"{info['subscribers']} subscribers, {info['videos']} videos.")
        print(f"[datapool] Item '{channel_handle}' marked as DONE.")

        maestro.finish_task(
            task_id=task_id,
            status=AutomationTaskFinishStatus.SUCCESS,
            message=f"'{channel_handle}': {info['subscribers']}, {info['videos']} videos.",
            total_items=1,
            processed_items=1,
            failed_items=0,
        )

        maestro.alert(
            task_id=task_id,
            title="Task finished successfully",
            message=f"Task finished for '{channel_handle}'.",
            alert_type=AlertType.INFO,
        )
        print("[ok] Task finished successfully.")

    except Exception as e:
        screenshot_path = "error_screenshot.png"
        try:
            bot.screenshot(filepath=screenshot_path)
        except Exception:
            screenshot_path = None

        maestro.error(
            task_id=int(task_id),
            exception=e,
            screenshot=screenshot_path,
            tags={"category": "youtube", "type": "unexpected-error"},
        )

        item.report_error(
            error_type=ErrorType.SYSTEM,
            finish_message=str(e),
        )

        maestro.finish_task(
            task_id=task_id,
            status=AutomationTaskFinishStatus.FAILED,
            message=f"Unexpected error: {e}",
            total_items=1,
            processed_items=0,
            failed_items=1,
        )
        raise

    finally:
        bot.stop_browser()


if __name__ == "__main__":
    action()
