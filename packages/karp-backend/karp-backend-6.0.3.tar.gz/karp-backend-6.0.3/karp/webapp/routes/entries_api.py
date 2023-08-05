import logging
from typing import Optional

from fastapi import (APIRouter, Depends, HTTPException, Response, Security,
                     status, Path, Query)
from starlette import responses
import structlog

from karp import errors as karp_errors, auth, lex
from karp.lex.application.queries import EntryViews, EntryDto, GetEntryHistory
from karp.lex.domain import commands, errors
from karp.auth import User
from karp.foundation.value_objects import PermissionLevel, unique_id
from karp.auth import AuthService
from karp.webapp import schemas, dependencies as deps

from karp.webapp.dependencies.fastapi_injector import inject_from_req

router = APIRouter()

logger = structlog.get_logger()


@router.get('/{resource_id}/{entry_id}/{version}', response_model=EntryDto, tags=["History"])
@router.get('/{resource_id}/{entry_id}', response_model=EntryDto, tags=["History"])
# @auth.auth.authorization("ADMIN")
def get_history_for_entry(
    resource_id: str,
    entry_id: str,
    version: Optional[int] = Query(None),
    user: auth.User = Security(deps.get_user, scopes=["admin"]),
    auth_service: auth.AuthService = Depends(deps.get_auth_service),
    get_entry_history: GetEntryHistory = Depends(deps.get_entry_history),
):
    log = logger.bind()
    if not auth_service.authorize(
        auth.PermissionLevel.admin, user, [resource_id]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": 'Bearer scope="lexica:admin"'},
        )
    log.info('getting history for entry', resource_id=resource_id,
             entry_id=entry_id, user=user)
    historical_entry = get_entry_history.query(
        resource_id, entry_id, version=version
    )

    return historical_entry


@router.post("/{resource_id}/add", status_code=status.HTTP_201_CREATED, tags=["Editing"])
@router.put('/{resource_id}', status_code=status.HTTP_201_CREATED, tags=["Editing"])
def add_entry(
    resource_id: str,
    data: schemas.EntryAdd,
    user: User = Security(deps.get_user, scopes=["write"]),
    auth_service: AuthService = Depends(deps.get_auth_service),
    adding_entry_uc: lex.AddingEntry = Depends(
        deps.get_lex_uc(lex.AddingEntry)),
):
    log = logger.bind()

    if not auth_service.authorize(PermissionLevel.write, user, [resource_id]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": 'Bearer scope="write"'},
        )
    log.info('adding entry', resource_id=resource_id, data=data)
    try:
        new_entry = adding_entry_uc.execute(
            commands.AddEntry(
                resource_id=resource_id,
                user=user.identifier,
                message=data.message,
                entry=data.entry,
            )
        )
    except errors.IntegrityError as exc:
        return responses.JSONResponse(
            status_code=400,
            content={
                'error': str(exc),
                'errorCode': karp_errors.ClientErrorCodes.DB_INTEGRITY_ERROR
            }
        )
    except errors.InvalidEntry as exc:
        return responses.JSONResponse(
            status_code=400,
            content={
                'error': str(exc),
                'errorCode': karp_errors.ClientErrorCodes.ENTRY_NOT_VALID
            }
        )

    return {"newID": new_entry.entry_id, "entityID": new_entry.entity_id}


@router.post("/{resource_id}/{entry_id}/update", tags=["Editing"])
@router.post('/{resource_id}/{entry_id}', tags=["Editing"])
# @auth.auth.authorization("WRITE", add_user=True)
def update_entry(
    response: Response,
    resource_id: str,
    entry_id: str,
    data: schemas.EntryUpdate,
    user: User = Security(deps.get_user, scopes=["write"]),
    auth_service: AuthService = Depends(deps.get_auth_service),
    updating_entry_uc: lex.UpdatingEntry = Depends(
        deps.get_lex_uc(lex.UpdatingEntry)),
):
    log = logger.bind()
    if not auth_service.authorize(PermissionLevel.write, user, [resource_id]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": 'Bearer scope="write"'},
        )

    #     force_update = convert.str2bool(request.args.get("force", "false"))
    #     data = request.get_json()
    #     version = data.get("version")
    #     entry = data.get("entry")
    #     message = data.get("message")
    #     if not (version and entry and message):
    #         raise KarpError("Missing version, entry or message")
    log.info('updating entry', resource_id=resource_id,
             entry_id=entry_id, data=data, user=user.identifier)
    try:
        entry = updating_entry_uc.execute(
            commands.UpdateEntry(
                resource_id=resource_id,
                entry_id=entry_id,
                version=data.version,
                user=user.identifier,
                message=data.message,
                entry=data.entry,
            )
        )
        # new_entry = entries.add_entry(
        #     resource_id, data.entry, user.identifier, message=data.message
        # )
        # new_id = entries.update_entry(
        #     resource_id,
        #     entry_id,
        #     data.version,
        #     data.entry,
        #     user.identifier,
        #     message=data.message,
        #     # force=force_update,
        # )
        return {"newID": entry.entry_id, "entityID": entry.entity_id}
    except errors.EntryNotFound:
        return responses.JSONResponse(
            status_code=404,
            content={
                'error': f"Entry '{entry_id}' not found in resource '{resource_id}' (version=latest)",
                'errorCode': karp_errors.ClientErrorCodes.ENTRY_NOT_FOUND,
                'resource': resource_id,
                'entry_id': entry_id,
            },
        )
    except errors.UpdateConflict as err:
        response.status_code = status.HTTP_400_BAD_REQUEST
        err.error_obj["errorCode"] = karp_errors.ClientErrorCodes.VERSION_CONFLICT
        return err.error_obj
    except Exception as err:
        logger.exception('error occured', resource_id=resource_id,
                         entry_id=entry_id, data=data)
        raise


@router.delete('/{resource_id}/{entry_id}/delete', tags=["Editing"])
@router.delete('/{resource_id}/{entry_id}', tags=["Editing"], status_code=status.)
# @auth.auth.authorization("WRITE", add_user=True)
def delete_entry(
    resource_id: str,
    entry_id: str,
    user: User = Security(deps.get_user, scopes=["write"]),
    auth_service: AuthService = Depends(deps.get_auth_service),
    deleting_entry_uc: lex.DeletingEntry = Depends(
        deps.get_lex_uc(lex.DeletingEntry))
):
    """Delete a entry from a resource.

    Arguments:
        user {karp.auth.user.User} -- [description]
        resource_id {str} -- [description]
        entry_id {str} -- [description]

    Returns:
        [type] -- [description]
    """
    if not auth_service.authorize(PermissionLevel.write, user, [resource_id]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": 'Bearer scope="write"'},
        )
    try:
        deleting_entry_uc.execute(
            commands.DeleteEntry(
                resource_id=resource_id,
                entry_id=entry_id,
                user=user.identifier,
            )
        )
    except errors.EntryNotFound:
        return responses.JSONResponse(
            status_code=404,
            content={
                'error': f"Entry '{entry_id}' not found in resource '{resource_id}' (version=latest)",
                'errorCode': karp_errors.ClientErrorCodes.ENTRY_NOT_FOUND,
                'resource': resource_id,
                'entry_id': entry_id,
            }
        )
    # entries.delete_entry(resource_id, entry_id, user.identifier)
    return "", 204


@router.post('/{resource_id}/preview')
# @auth.auth.authorization("READ")
def preview_entry(
    resource_id: str,
):
    pass
#     data = request.get_json()
#     preview = entrywrite.preview_entry(resource_id, data)
#     return flask_jsonify(preview)


def init_app(app):
    app.include_router(router)
