#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Return a dictionary (or list) of pipe objects. See documentation below for more information.
"""

from __future__ import annotations

from meerschaum.utils.typing import (
    Sequence, Optional, Union, Mapping, Any, InstanceConnector, PipesDict, List, Dict, Tuple
)

def get_pipes(
        connector_keys: Optional[Union[str, List[str]]] = None,
        metric_keys: Optional[Union[str, List[str]]] = None,
        location_keys: Optional[Union[str, List[str]]] = None,
        params: Optional[Dict[str, Any]] = None,
        mrsm_instance: Union[str, InstanceConnector, None] = None,
        instance: Union[str, InstanceConnector, None] = None,
        as_list: bool = False,
        method: str = 'registered',
        wait: bool = False,
        debug: bool = False,
        **kw: Any
    ) -> Union[PipesDict, List['meerschaum.Pipe']]:
    """Return a dictionary (or list) of pipe objects.
    The pipes dictionary returned from `meerschaum.utils.get_pipes` has the following format:
    
    ```
    
    **NOTE:** If a pipe does not have a `location` key, it must be referenced as `None`.
    E.g. The pipe `sql:main_weather` would look like this:
    
    ```

    Parameters
    ----------
    connector_keys :
        String or list of connector keys.
        If parameter is omitted or is '*', fetch all connector_keys.
    metric_keys :
        String or list of metric keys.
        See connector_keys for formatting
    location_keys :
        String or list of location keys.
        See connector_keys for formatting
    params :
        Dictionary of additional parameters to search by.
        Params are parsed into a SQL WHERE clause.
        E.g. { 'a' : 1, 'b' : 2 } equates to 'WHERE a = 1 AND b = 2'
    mrsm_instance :
        Connector keys for the Meerschaum instance of the pipes.
        Must be of SQLConnector or APIConnector and point to a valid
        Meerschaum instance.
    as_list :
        If True, return pipes in a list instead of a hierarchical dictionary.
        False : { connector_keys : { metric_key : { location_key : Pipe } } }
        True  : [ Pipe ]
        Defaults to False.
    method :
        registered', 'explicit', 'all']
        
        If 'registered' (default), create pipes based on registered keys in the connector's pipes table
        (API or SQL connector, depends on mrsm_instance).
        
        If 'explicit', create pipes from provided connector_keys, metric_keys, and location_keys
        instead of consulting the pipes table. Useful for creating non-existent pipes.
        
        If 'all', create pipes from predefined metrics and locations. Required connector_keys.
        **NOTE:** Not implemented!
    wait :
        Wait for a connection before getting Pipes. Should only be true for cases where the
        database might not be running (like the API).
    connector_keys: Optional[Union[str :
        
    List[str]]] :
         (Default value = None)
    metric_keys: Optional[Union[str :
        
    location_keys: Optional[Union[str :
        
    params: Optional[Dict[str :
        
    Any]] :
         (Default value = None)
    mrsm_instance: Union[str :
        
    InstanceConnector :
        
    None] :
         (Default value = None)
    instance: Union[str :
        
    as_list: bool :
         (Default value = False)
    method: str :
         (Default value = 'registered')
    wait: bool :
         (Default value = False)
    debug: bool :
         (Default value = False)
    **kw: Any :
        

    Returns
    -------

    >>> pipes = {
    ...     <connector_keys> : {
    ...         <metric> : {
    ...             <location> : Pipe(
    ...                 <connector_keys>,
    ...                 <metric>,
    ...                 <location>,
    ...             ),
    ...         },
    ...     },
    ... },
    >>>
    ```
    
    >>> pipes['sql:main']['weather'][None]
    ```
    """

    from meerschaum.config import get_config
    from meerschaum.utils.warnings import error
    from meerschaum.utils.misc import filter_keywords

    if connector_keys is None:
        connector_keys = []
    if metric_keys is None:
        metric_keys = []
    if location_keys is None:
        location_keys = []
    if params is None:
        params = {}

    if isinstance(connector_keys, str):
        connector_keys = [connector_keys]
    if isinstance(metric_keys, str):
        metric_keys = [metric_keys]
    if isinstance(location_keys, str):
        location_keys = [location_keys]

    ### Get SQL or API connector (keys come from `connector.fetch_pipes_keys()`).
    ### If `wait`, wait until a connection is made
    if mrsm_instance is None:
        mrsm_instance = instance
    if mrsm_instance is None:
        mrsm_instance = get_config('meerschaum', 'instance', patch=True)
    if isinstance(mrsm_instance, str):
        from meerschaum.connectors.parse import parse_instance_keys
        connector = parse_instance_keys(keys=mrsm_instance, wait=wait, debug=debug)
    else: ### NOTE: mrsm_instance MUST be a SQL or API connector for this to work
        from meerschaum.connectors import Connector
        valid_connector = False
        if issubclass(type(mrsm_instance), Connector):
            if mrsm_instance.type in ('api', 'sql'):
                valid_connector = True
        if not valid_connector:
            error(f"Invalid instance connector: {mrsm_instance}")
        connector = mrsm_instance
    if debug:
        from meerschaum.utils.debug import dprint
        dprint(f"Using instance connector: {connector}")
    if not connector:
        error(f"Could not create connector from keys: '{mrsm_instance}'")

    ### get a list of tuples of keys based on the method type
    result = methods(
        method,
        connector,
        connector_keys = connector_keys,
        metric_keys = metric_keys,
        location_keys = location_keys,
        params = params,
        debug = debug
    )
    if result is None:
        error(f"Unable to build pipes!")

    ### populate the `pipes` dictionary with Pipes based on the keys
    ### obtained from the chosen `method`.
    from meerschaum import Pipe
    pipes = dict()
    for ck, mk, lk in result:
        if ck not in pipes:
            pipes[ck] = {}

        if mk not in pipes[ck]:
            pipes[ck][mk] = {}

        pipes[ck][mk][lk] = Pipe(
            ck, mk, lk,
            mrsm_instance=connector,
            debug=debug,
            **filter_keywords(Pipe, **kw)
        )

    if not as_list:
        return pipes
    from meerschaum.utils.misc import flatten_pipes_dict
    return flatten_pipes_dict(pipes)

def methods(
        method: str,
        connector: 'meerschaum.connectors.Connector',
        **kw: Any
    ) -> List[Tuple[str, str, str]]:
    """

    Parameters
    ----------
    method: str :
        
    connector: 'meerschaum.connectors.Connector' :
        
    **kw: Any :
        

    Returns
    -------
    type
        based on the method of choosing keys.

    """
    from meerschaum.utils.warnings import error
    from meerschaum.connectors.sql.tables import get_tables
    tables = get_tables(connector)

    def _registered(
            connector_keys : Optional[List[str]] = None,
            metric_keys : Optional[List[str]] = None,
            location_keys : Optional[List[str]] = None,
            params : Optional[Dict[str, Any]] = None,
            debug : bool = False,
            **kw
        ) -> List[Tuple[str, str, str]]:
        """Get keys from the pipes table or the API directly.
        Builds query or URL based on provided keys and parameters.
        
        Only works for SQL and API Connectors.

        Parameters
        ----------
        connector_keys : Optional[List[str]] :
             (Default value = None)
        metric_keys : Optional[List[str]] :
             (Default value = None)
        location_keys : Optional[List[str]] :
             (Default value = None)
        params : Optional[Dict[str :
            
        Any]] :
             (Default value = None)
        debug : bool :
             (Default value = False)
        **kw :
            

        Returns
        -------

        """
        if connector_keys is None:
            connector_keys = []
        if metric_keys is None:
            metric_keys = []
        if location_keys is None:
            location_keys = []
        if params is None:
            params = {}

        return connector.fetch_pipes_keys(
            connector_keys = connector_keys,
            metric_keys = metric_keys,
            location_keys = location_keys,
            params = params,
            debug = debug
        )

    def _explicit(
            connector_keys : Optional[List[str]] = None,
            metric_keys : Optional[List[str]] = None,
            location_keys : Optional[List[str]] = None,
            params : Optional[Dict[str, Any]] = None,
            debug : bool = False,
            **kw
        ) -> List[Tuple[str, str, str]]:
        """Explicitly build Pipes based on provided keys.
        Raises an error if connector_keys or metric_keys is empty,
        and assumes location_keys = [None] if empty.

        Parameters
        ----------
        connector_keys : Optional[List[str]] :
             (Default value = None)
        metric_keys : Optional[List[str]] :
             (Default value = None)
        location_keys : Optional[List[str]] :
             (Default value = None)
        params : Optional[Dict[str :
            
        Any]] :
             (Default value = None)
        debug : bool :
             (Default value = False)
        **kw :
            

        Returns
        -------

        """

        if connector_keys is None:
            connector_keys = []
        if metric_keys is None:
            metric_keys = []
        if location_keys is None:
            location_keys = []
        if params is None:
            params = {}

        if not isinstance(connector_keys, list):
            connector_keys = [connector_keys]
        if not isinstance(metric_keys, list):
            metric_keys = [metric_keys]
        if not isinstance(location_keys, list):
            location_keys = [location_keys]

        missing_keys = []
        if len(connector_keys) == 0:
            missing_keys.append('connector_keys')
        if len(metric_keys) == 0:
            missing_keys.append('metric_keys')
        if len(location_keys) == 0:
            location_keys.append(None)
        if len(missing_keys) > 0:
            error_message = "Missing parameters: '" + "', '".join(missing_keys) + "'"
            error_message += "\nSee --help for information for passing parameters."
            error(error_message)
        result = []
        for ck in connector_keys:
            for mk in metric_keys:
                for lk in location_keys:
                    result.append((ck, mk, lk))
        return result

    def _all(**kw):
        """Fetch all available metrics and locations and create every combination.
        Connector keys are required.

        Parameters
        ----------
        **kw :
            

        Returns
        -------

        """
        error(
            "Need to implement metrics and locations logic in SQL and API.",
            NotImplementedError
        )

    _methods = {
        'registered' : _registered,
        'explicit'   : _explicit,
        'all'        : _all,
        ### TODO implement 'all'
    }
    if method not in _methods:
        error(f"Method '{method}' is not supported!", NotImplementedError)
    return _methods[method](**kw)
