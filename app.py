"""ANT-OS Streamlit Demo — context display + host controls."""

from __future__ import annotations

import streamlit as st

import ant_connect_streamlit as ant_connect

st.set_page_config(page_title="ANT Streamlit Demo", page_icon=":link:", layout="wide")


def navigate_widget(ant: ant_connect.AntConnect) -> None:
    st.subheader(":compass: Navigate")

    tab_quick, tab_app, tab_fav = st.tabs(["Quick", "App", "Favorite"])

    with tab_quick:
        cols = st.columns(3)
        with cols[0]:
            if st.button(":house: Dashboard", key="nav_dash", use_container_width=True):
                ant.send_signal({"navigate": {"to": "OS.dash"}})
        with cols[1]:
            if st.button(":door: Login", key="nav_login", use_container_width=True):
                ant.send_signal({"navigate": {"to": "OS.login"}})
        with cols[2]:
            if st.button(":bust_in_silhouette: Profile", key="nav_profile", use_container_width=True):
                ant.send_signal({"navigate": {"to": "OS.profile"}})

    with tab_app:
        method = st.radio("Method", ["push", "replace"], horizontal=True, key="nav_method")
        col_id, col_title = st.columns(2)
        with col_id:
            app_id = st.text_input("App ID", key="nav_app_id")
            if st.button("Go by ID", key="nav_go_id", use_container_width=True) and app_id:
                ant.send_signal({"navigate": {"to": {"app": {"id": app_id}}, "method": method}})
        with col_title:
            app_title = st.text_input("App title (search)", key="nav_app_title")
            if st.button("Go by title", key="nav_go_title", use_container_width=True) and app_title:
                ant.send_signal({"navigate": {"to": {"app": {"title": app_title}}, "method": method}})

    with tab_fav:
        fav_idx = st.number_input("Favorite index", min_value=0, step=1, key="nav_fav_idx")
        if st.button("Go to favorite", key="nav_go_fav", use_container_width=True):
            ant.send_signal({"navigate": {"to": {"app": {"favorite": int(fav_idx)}}}})


def main() -> None:
    ant = ant_connect.connect()
    ctx = ant.context

    if ctx is None:
        st.info("Waiting for ANT-OS context...")
        return

    project = ctx.project
    license_ = ctx.license
    user = ctx.user

    with st.sidebar:
        st.header(":link: ANT-OS Context")
        if user:
            st.write(f":bust_in_silhouette: **{user.firstname} {user.lastname}**")
        if license_:
            st.write(f":key: {license_.name}")
        if project:
            st.write(f":office: {project.name}")
        else:
            st.warning("No project selected")

        st.divider()
        st.subheader(":joystick: Host Controls")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(":memo: Notepad", use_container_width=True):
                ant.send_signal({"notepad": {"action": "toggle"}})
        with col2:
            if st.button(":eye: Overlay", use_container_width=True):
                ant.send_signal({"overlay": {"action": True}})
        with col3:
            if st.button(":1234: Count", key="count_btn", use_container_width=True):
                ant.send_signal({"_action": "increment_title"})

        st.divider()
        st.subheader(":bell: Notifications")
        notif_col1, notif_col2 = st.columns(2)
        with notif_col1:
            if st.button(":white_check_mark: Success", key="notif_ok", use_container_width=True):
                ant.notify("Operation completed!", type="success")
            if st.button(":warning: Warning", key="notif_warn", use_container_width=True):
                ant.notify("Check your input", type="warning")
        with notif_col2:
            if st.button(":x: Error", key="notif_err", use_container_width=True):
                ant.notify("Something went wrong", type="error")
            if st.button(":information_source: Info", key="notif_info", use_container_width=True):
                ant.notify("FYI: task updated", type="info")

    ant.set_toolbar(
        title="Streamlit Demo",
        subtitle=project.name if project else None,
        menu=[
            {"icon": "mdi-information", "title": "About", "notify": "ANT-OS Streamlit Demo v1.0"},
            {"icon": "mdi-counter", "title": "Count", "action": "increment_title"},
        ],
    )

    st.title(":link: ANT-OS Streamlit Demo")

    if project:
        st.success(f"Connected to project: **{project.name}**")

    navigate_widget(ant)

    st.divider()
    st.subheader(":globe_with_meridians: HTTP Request Proxy")
    if project:
        endpoints = [
            f"api/2.0/projects/{project.id}",
            f"api/2.0/projects/{project.id}/users",
        ]
    else:
        endpoints = ["api/2.0/projects/nonexistent-id"]
    req_url = st.selectbox("Endpoint", endpoints, key="req_url")
    if st.button("Fetch", key="req_send", use_container_width=True):
        ant.clear_request_cache()
        st.session_state["_req_fire"] = True
        st.session_state.pop("_req_result", None)
        st.session_state.pop("_req_error", None)

    if st.session_state.get("_req_fire"):
        result = ant.request(req_url).response({
            "onSuccess": lambda d: st.session_state.update(_req_result=d, _req_error=None),
            "onError": lambda e: st.session_state.update(_req_error=e, _req_result=None),
        })
        if result is None:
            st.info("Request queued — waiting for host response...")
        else:
            st.session_state["_req_fire"] = False

    if st.session_state.get("_req_error"):
        st.error(f"Error: {st.session_state['_req_error']}")
    elif st.session_state.get("_req_result"):
        st.json(st.session_state["_req_result"])

    st.divider()
    st.subheader(":satellite: Real-Time Observer")

    if project:
        if "observer_key" not in st.session_state:
            st.session_state.observer_key = ant.observe("task")
            st.session_state.event_log = []

        for event in ant.events("task"):
            st.session_state.event_log.insert(0, event)
            st.session_state.event_log = st.session_state.event_log[:20]

        col_clear, col_stop = st.columns(2)
        with col_clear:
            if st.button(":wastebasket: Clear log", key="clear_events", use_container_width=True):
                st.session_state.event_log = []
        with col_stop:
            if st.button(":stop_sign: Stop observing", key="stop_obs", use_container_width=True):
                key = st.session_state.pop("observer_key", None)
                if key:
                    ant.unobserve(key)
                    st.success("Observer stopped")

        if st.session_state.get("event_log"):
            for ev in st.session_state.event_log:
                task_data = ev.get("task", ev)
                action = task_data.get("action", "?")
                tid = task_data.get("id", "?")
                title = task_data.get("data", {}).get("title", "") if isinstance(task_data.get("data"), dict) else ""
                st.write(f"**{action}** task `{tid}`" + (f" — _{title}_" if title else ""))
                with st.expander("Raw signal data"):
                    st.json(ev)
        else:
            st.info("Listening for task changes... Edit a task in another tab to see events here.")
    else:
        st.warning("Select a project to start observing task changes")

    st.caption("Use the sidebar and controls to interact with ANT-OS host features.")


main()
