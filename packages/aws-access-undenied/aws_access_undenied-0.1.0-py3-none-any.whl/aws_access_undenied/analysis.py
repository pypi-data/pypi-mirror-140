import json
from typing import (
    Dict,
    Any,
    Optional,
    TextIO,
    Union,
)

import botocore.exceptions
from aws_error_utils import errors

from aws_access_undenied import common
from aws_access_undenied import event
from aws_access_undenied import event_permission_data
from aws_access_undenied import iam_policy_data
from aws_access_undenied import logger
from aws_access_undenied import results
from aws_access_undenied import result_details
from aws_access_undenied import simulate_custom_policy_context_generator
from aws_access_undenied import simulate_custom_policy_helper
from aws_access_undenied.results import AnalysisResult


def _analyze_and_output_result(config: common.Config, raw_event: Dict[str, Any]) -> None:
    if raw_event.get("errorCode") not in [
        "AccessDenied",
        "Client.UnauthorizedOperation",
    ]:
        logger.debug(
            "Event without AccessDenied/Client.UnauthorizedOperation"
            " error code not handled:"
            f" [eventID:{raw_event['eventID']}, "
            f"errorCode:{raw_event.get('errorCode')}]"
        )
        return None

    event_ = event.Event(raw_event)
    logger.info("AccessDenied cloudtrail_event found:" f" [eventID={event_.event_id}]")
    logger.debug(f"[errorMessage:{event_.error_message}]")

    if _is_valid_encoded_message(event_.error_message):
        try:
            _write_to_output(
                config,
                _handle_encoded_message(config, event_.error_message),
            )
            return
        except (
            errors.InvalidAuthorizationMessageException,
        ) as invalid_authorization_message_exception:
            logger.debug(
                "Could not decode authorization message:"
                f" {invalid_authorization_message_exception}. Continuing"
                " analysis as usual."
            )

    try:
        logger.debug(
            "Analyzing event permission data (event Principal, Action,"
            " Resources, and Conditions)..."
        )
        event_permission_data_ = event_permission_data.EventPermissionData.from_event(
            event_, config
        )
        if event_permission_data_.is_missing_allow_in_identity_based_policy:
            logger.debug(
                "Quick-exit condition: simple missing allow in identity-based"
                " policy with all parameters known."
            )
            _write_to_output(
                config,
                _create_simple_missing_allow_analysis_result(
                    cloudtrail_event_=event_,
                    event_permission_data_=event_permission_data_,
                ),
            )
            return

        logger.debug("Gathering all relevant IAM policies for permission analysis...")
        iam_policy_data_ = iam_policy_data.IamPolicyData.from_event_permission_data(
            config=config,
            event_permission_data_=event_permission_data_,
            region=event_.region,
        )

        logger.debug("Generating context values for condition assessment...")
        context = simulate_custom_policy_context_generator.SimulateCustomPolicyContextGenerator(
            session=config.session,
            event_permission_data_=event_permission_data_,
            cloudtrail_event_=event_,
        ).generate_context(
            simulate_custom_policy_helper.generate_context_key_list_for_simulate_custom_policy(
                iam_policy_data_, config.iam_client
            )
        )

        logger.debug(
            "Calling iam:SimulateCustomPolicy with the relevant arguments"
            " and analyzing the responses..."
        )
        simulate_custom_policy_request = (
            simulate_custom_policy_helper.generate_simulate_custom_policy_request(
                iam_policy_data_=iam_policy_data_,
                event_permission_data_=event_permission_data_,
                context=context,
            )
        )
        analysis_result = simulate_custom_policy_helper.simulate_custom_policies(
            config.iam_client,
            event_,
            event_permission_data_,
            iam_policy_data_,
            simulate_custom_policy_request,
        )
        if analysis_result:
            _write_to_output(config, analysis_result)
            return
    except common.AccessUndeniedError as invalid_authorization_message_exception:
        logger.error(
            str(invalid_authorization_message_exception)
            + f" [eventID:{raw_event.get('eventID', '<None>')}]"
        )
        _write_to_output(
            config,
            results.ErrorResult(
                event_id=raw_event.get("eventID", "<None>"),
                assessment_result=invalid_authorization_message_exception.access_denied_reason,
                error_message=str(invalid_authorization_message_exception),
            ),
        )
        return
    except (
        errors.AccessDenied,
        botocore.exceptions.ClientError,
    ) as invalid_authorization_message_exception:
        logger.error(
            repr(invalid_authorization_message_exception)
            + f" [eventID:{raw_event.get('eventID', '<None>')}]"
        )
        _write_to_output(
            config,
            results.ErrorResult(
                event_id=raw_event.get("eventID", "<None>"),
                assessment_result=common.AccessDeniedReason.ERROR,
                error_message=str(invalid_authorization_message_exception),
            ),
        )
        return


def _write_to_file(output_file: TextIO, output_json: Dict[str, Any]) -> None:
    if output_file is not None and output_file:
        output_file.write(json.dumps(output_json, indent=2))
        output_file.close()


def _handle_encoded_message(
    config: common.Config, error_message: str
) -> Optional[Dict[str, Any]]:
    # Handle the case of EC2 encoded message, decode the message and output the result
    # https://docs.aws.amazon.com/STS/latest/APIReference/API_DecodeAuthorizationMessage.html
    logger.debug("Encoded EC2 Authorization error message present, attempt to decode")
    return json.loads(
        config.session.client("sts").decode_authorization_message(
            EncodedMessage=error_message.split("Encoded authorization failure message: ")[
                -1
            ]
        )["DecodedMessage"]
    )


def _is_valid_encoded_message(error_message) -> bool:
    if error_message and "Encoded authorization failure message" in error_message:
        if error_message[-3:] == "...":
            logger.error(
                "Could not decode authorization message because the message"
                " in the CloudTrail event is incomplete. CloudTrail does"
                " not store error messages longer than 1024 chars."
                " Attempting regular analysis."
            )
            return False
        return True


def _write_to_output(
    config: common.Config,
    result: Union[Dict[str, Any], results.Result],
) -> None:
    """
    Output result to file, stdout, or both - as per the configuration.
    """
    if not config.suppress_output:
        print(str(result))
    if config.output_file:
        config.output_json.get("Results", []).append(json.loads(str(result)))


def analyze_cloudtrail_events(config: common.Config, raw_events_file_path):
    raw_events = json.load(raw_events_file_path)
    # Multiple CloudTrail log records in file or single event
    for raw_event in raw_events.get("Records") or [raw_events]:
        _analyze_and_output_result(config, raw_event)
    _write_to_file(config.output_file, config.output_json)


def _create_simple_missing_allow_analysis_result(
    cloudtrail_event_: event.Event,
    event_permission_data_: event_permission_data.EventPermissionData,
) -> AnalysisResult:
    return AnalysisResult(
        event_id=cloudtrail_event_.event_id,
        assessment_result=common.AccessDeniedReason.IDENTITY_POLICY_MISSING_ALLOW,
        result_details_=result_details.MissingAllowResultDetails(
            simulate_custom_policy_response={
                "EvalActionName": event_permission_data_.iam_permission,
                "EvalResourceName": event_permission_data_.resource.arn,
                "EvalDecision": "implicitDeny",
                "MatchedStatements": [],
                "MissingContextValues": [],
            },
            missing_allow_reason=common.AccessDeniedReason.IDENTITY_POLICY_MISSING_ALLOW,
            target_resource_arn=event_permission_data_.resource.arn,
            target_principal_arn=event_permission_data_.principal.arn,
        ),
    )
