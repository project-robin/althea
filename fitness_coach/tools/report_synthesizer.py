"""Tool for synthesizing meal and workout reports."""

from google.adk.tools import FunctionTool, ToolContext
from typing import Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

def synthesize_report(tool_context: ToolContext) -> Union[str, Dict[str, Any]]:
    """
    Synthesizes a comprehensive report from generated meal and workout plans stored in session state.

    Args:
        tool_context: The tool context containing session state.

    Returns:
        A formatted string containing the combined meal and workout report, or an error status.
    """
    try:
        meal_plan = tool_context.state.get('meal_plan_result', 'No meal plan generated.')
        workout_plan = tool_context.state.get('workout_plan_result', 'No workout plan generated.')

        report = "## Your Personalized Fitness Report\n\n"

        if meal_plan != 'No meal plan generated.':
            report += "### Meal Plan\n\n"
            report += meal_plan + "\n\n"

        if workout_plan != 'No workout plan generated.':
            report += "### Workout Plan\n\n"
            report += workout_plan + "\n\n"

        if meal_plan == 'No meal plan generated.' and workout_plan == 'No workout plan generated.':
             report += "No plans were generated in this session."

        return report
    except Exception as e:
        logger.error(f"Error synthesizing report: {e}")
        return {"status": "error", "message": "An error occurred while synthesizing the report."}

report_synthesizer_tool = FunctionTool(
    func=synthesize_report
) 