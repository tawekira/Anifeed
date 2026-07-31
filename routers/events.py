from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models import EventStatus, Event
from db import get_session, get_current_user

def create_event(
        user_id: int, 
        anime_id: int, 
        event_type: EventStatus,
        event_metadata: dict
):
    event = EventStatus(
        user_id = user_id,
        anime_id = anime_id,
        event_type = event_type,
        event_metadata = event_metadata
    )
    session = get_session()
    session.add(event)
    session.commit()


    