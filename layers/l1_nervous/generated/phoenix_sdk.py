from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para phoenix
# NO EDITAR DIRECTAMENTE.

class PhoenixClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def list_prompts(self, **kwargs) -> Any:
        """Get a list of all the prompts.  Prompts (templates, prompt templates) are versioned templates for input messages to an LLM. Each prompt includes both the input messages, but also the model and invocation parameters to use when generating outputs.  Returns a list of prompt objects with their IDs, names, and descriptions.  Example usage:   List all available prompts  Expected return:   Array of prompt objects with metadata.   Example:  [{       "name": "article-summarizer",       "description": "Summarizes an article into concise bullet points",       "source_prompt_id": null,       "id": "promptid1234"   }]"""
        return await self.proxy.call_tool('phoenix', 'list-prompts', kwargs)

    async def get_prompt(self, **kwargs) -> Any:
        """Get a prompt using a single MCP-native interface.  Provide a prompt identifier to fetch the latest version, or add a tag or versionId to select a specific version.  Example usage:   Get prompt "article-summarizer"   Get prompt "article-summarizer" with tag "production"   Get prompt "article-summarizer" using version "promptversionid1234"  Expected return:   Prompt version object with template and configuration."""
        return await self.proxy.call_tool('phoenix', 'get-prompt', kwargs)

    async def get_latest_prompt(self, **kwargs) -> Any:
        """Get the latest version of a prompt. Returns the prompt version with its template, model configuration, and invocation parameters.  Example usage:   Get the latest version of a prompt named 'article-summarizer'  Expected return:   Prompt version object with template and configuration.   Example: {     "description": "Initial version",     "model_provider": "OPENAI",     "model_name": "gpt-3.5-turbo",     "template": {       "type": "chat",       "messages": [         {           "role": "system",           "content": "You are an expert summarizer. Create clear, concise bullet points highlighting the key information."         },         {           "role": "user",           "content": "Please summarize the following {{topic}} article:\n\n{{article}}"         }       ]     },     "template_type": "CHAT",     "template_format": "MUSTACHE",     "invocation_parameters": {       "type": "openai",       "openai": {}     },     "id": "promptversionid1234"   }"""
        return await self.proxy.call_tool('phoenix', 'get-latest-prompt', kwargs)

    async def get_prompt_by_identifier(self, **kwargs) -> Any:
        """Get a prompt's latest version by its identifier (name or ID). Returns the prompt version with its template, model configuration, and invocation parameters.  Example usage:   Get the latest version of a prompt with name 'article-summarizer'  Expected return:   Prompt version object with template and configuration."""
        return await self.proxy.call_tool('phoenix', 'get-prompt-by-identifier', kwargs)

    async def get_prompt_version(self, **kwargs) -> Any:
        """Get a specific version of a prompt using its version ID. Returns the prompt version with its template, model configuration, and invocation parameters.  Example usage:   Get a specific prompt version with ID 'promptversionid1234'  Expected return:   Prompt version object with template and configuration."""
        return await self.proxy.call_tool('phoenix', 'get-prompt-version', kwargs)

    async def upsert_prompt(self, **kwargs) -> Any:
        """Create or update a prompt with its template and configuration. Creates a new prompt and its initial version with specified model settings.  Example usage:   Create a new prompt named 'email_generator' with a template for generating emails  Expected return:   A confirmation message of successful prompt creation"""
        return await self.proxy.call_tool('phoenix', 'upsert-prompt', kwargs)

    async def list_prompt_versions(self, **kwargs) -> Any:
        """Get a list of all versions for a specific prompt. Returns versions with pagination support.  Example usage:   List all versions of a prompt named 'article-summarizer'  Expected return:   Array of prompt version objects with IDs and configuration."""
        return await self.proxy.call_tool('phoenix', 'list-prompt-versions', kwargs)

    async def get_prompt_version_by_tag(self, **kwargs) -> Any:
        """Get a prompt version by its tag name. Returns the prompt version with its template, model configuration, and invocation parameters.  Example usage:   Get the 'production' tagged version of prompt 'article-summarizer'  Expected return:   Prompt version object with template and configuration."""
        return await self.proxy.call_tool('phoenix', 'get-prompt-version-by-tag', kwargs)

    async def list_prompt_version_tags(self, **kwargs) -> Any:
        """Get a list of all tags for a specific prompt version. Returns tag objects with pagination support.  Example usage:   List all tags associated with prompt version 'promptversionid1234'  Expected return:   Array of tag objects with names and IDs."""
        return await self.proxy.call_tool('phoenix', 'list-prompt-version-tags', kwargs)

    async def add_prompt_version_tag(self, **kwargs) -> Any:
        """Add a tag to a specific prompt version. The operation returns no content on success (204 status code).  Example usage:   Tag prompt version 'promptversionid1234' with the name 'production'  Expected return:   Confirmation message of successful tag addition"""
        return await self.proxy.call_tool('phoenix', 'add-prompt-version-tag', kwargs)

    async def list_experiments_for_dataset(self, **kwargs) -> Any:
        """Get a list of all the experiments run on a given dataset.  Experiments are collections of experiment runs, each experiment run corresponds to a single dataset example. The dataset example is passed to an implied `task` which in turn produces an output.  Example usage:   Show me all the experiments I've run on dataset RGF0YXNldDox  Expected return:   Array of experiment objects with metadata.   Example: [     {       "id": "experimentid1234",       "dataset_id": "datasetid1234",       "dataset_version_id": "datasetversionid1234",       "repetitions": 1,       "metadata": {},       "project_name": "Experiment-abc123",       "created_at": "YYYY-MM-DDTHH:mm:ssZ",       "updated_at": "YYYY-MM-DDTHH:mm:ssZ"     }   ]"""
        return await self.proxy.call_tool('phoenix', 'list-experiments-for-dataset', kwargs)

    async def get_experiment_by_id(self, **kwargs) -> Any:
        """Get an experiment by its ID.  The tool returns experiment metadata in the first content block and a JSON object with the experiment data in the second. The experiment data contains both the results of each experiment run and the annotations made by an evaluator to score or label the results, for example, comparing the output of an experiment run to the expected output from the dataset example.  Example usage:   Show me the experiment results for experiment RXhwZXJpbWVudDo4  Expected return:   Object containing experiment metadata and results."""
        return await self.proxy.call_tool('phoenix', 'get-experiment-by-id', kwargs)

    async def list_datasets(self, **kwargs) -> Any:
        """Get a list of all datasets.  Datasets are collections of 'dataset examples' that each example includes an input, (expected) output, and optional metadata. They are primarily used as inputs for experiments.  Example usage:   Show me all available datasets  Expected return:   Array of dataset objects with metadata.   Example: [     {       "id": "RGF0YXNldDox",       "name": "my-dataset",       "description": "A dataset for testing",       "metadata": {},       "created_at": "2024-03-20T12:00:00Z",       "updated_at": "2024-03-20T12:00:00Z"     }   ]"""
        return await self.proxy.call_tool('phoenix', 'list-datasets', kwargs)

    async def get_dataset(self, **kwargs) -> Any:
        """Get dataset metadata by name or ID.  Example usage:   Show me the dataset "my-dataset"  Expected return:   A dataset object with metadata and version information."""
        return await self.proxy.call_tool('phoenix', 'get-dataset', kwargs)

    async def get_dataset_examples(self, **kwargs) -> Any:
        """Get examples from a dataset.  Dataset examples are an array of objects that each include an input, (expected) output, and optional metadata. These examples are typically used to represent input to an application or model (e.g. prompt template variables, a code file, or image) and used to test or benchmark changes.  Example usage:   Show me all examples from dataset RGF0YXNldDox  Expected return:   Object containing dataset ID, version ID, and array of examples."""
        return await self.proxy.call_tool('phoenix', 'get-dataset-examples', kwargs)

    async def get_dataset_experiments(self, **kwargs) -> Any:
        """List experiments run on a dataset.  Example usage:   Show me all experiments run on dataset RGF0YXNldDox  Expected return:   Array of experiment objects with metadata."""
        return await self.proxy.call_tool('phoenix', 'get-dataset-experiments', kwargs)

    async def add_dataset_examples(self, **kwargs) -> Any:
        """Add examples to an existing dataset.  This tool adds one or more examples to an existing dataset. Each example includes an input, output, and metadata. The metadata will automatically include information indicating that these examples were synthetically generated via MCP. When calling this tool, check existing examples using the "get-dataset-examples" tool to ensure that you are not adding duplicate examples and following existing patterns for how data should be structured.  Example usage:   Look at the analyze "my-dataset" and augment them with new examples to cover relevant edge cases  Expected return:   Confirmation of successful addition of examples to the dataset."""
        return await self.proxy.call_tool('phoenix', 'add-dataset-examples', kwargs)

    async def list_projects(self, **kwargs) -> Any:
        """Get a list of all projects.  Projects are containers for organizing traces, spans, and other observability data. Each project has a unique name and can contain traces from different applications or experiments.  Example usage:   Show me all available projects  Expected return:   Array of project objects with metadata.   Example: [     {       "id": "UHJvamVjdDox",       "name": "default",       "description": "Default project for traces"     },     {       "id": "UHJvamVjdDoy",       "name": "my-experiment",       "description": "Project for my ML experiment"     }   ]"""
        return await self.proxy.call_tool('phoenix', 'list-projects', kwargs)

    async def get_project(self, **kwargs) -> Any:
        """Get a project by name or ID.  Example usage:   Show me the project "default"  Expected return:   A single project object with metadata."""
        return await self.proxy.call_tool('phoenix', 'get-project', kwargs)

    async def list_traces(self, **kwargs) -> Any:
        """List traces for a project.  This tool groups project spans into traces and returns the newest traces first.  Example usage:   Show me the last 10 traces for project "default"   Show me recent traces from the last 30 minutes for project "checkout"  Expected return:   Array of trace objects with grouped spans and summary timing information."""
        return await self.proxy.call_tool('phoenix', 'list-traces', kwargs)

    async def get_trace(self, **kwargs) -> Any:
        """Get a single trace by its exact trace ID within a project.  Example usage:   Show me trace "abc123def456" from project "default"  Expected return:   A trace object with all spans that belong to the trace."""
        return await self.proxy.call_tool('phoenix', 'get-trace', kwargs)

    async def get_spans(self, **kwargs) -> Any:
        """Get spans from a project with filtering criteria.  Spans represent individual operations or units of work within a trace. They contain timing information, attributes, and context about the operation being performed.  Example usage:   Get recent spans from project "my-project"   Get spans in a time range from project "my-project"  Expected return:   Object containing spans array and optional next cursor for pagination.   Example: {     "spans": [       {         "id": "span123",         "name": "http_request",         "context": {           "trace_id": "trace456",           "span_id": "span123"         },         "start_time": "2024-01-01T12:00:00Z",         "end_time": "2024-01-01T12:00:01Z",         "attributes": {           "http.method": "GET",           "http.url": "/api/users"         }       }     ],     "nextCursor": "cursor_for_pagination"   }"""
        return await self.proxy.call_tool('phoenix', 'get-spans', kwargs)

    async def get_span_annotations(self, **kwargs) -> Any:
        """Get span annotations for a list of span IDs.  Span annotations provide additional metadata, scores, or labels for spans. They can be created by humans, LLMs, or code and help in analyzing and categorizing spans.  Example usage:   Get annotations for spans ["span1", "span2"] from project "my-project"   Get quality score annotations for span "span1" from project "my-project"  Expected return:   Object containing annotations array and optional next cursor for pagination.   Example: {     "annotations": [       {         "id": "annotation123",         "span_id": "span1",         "name": "quality_score",         "result": {           "label": "good",           "score": 0.95,           "explanation": null         },         "annotator_kind": "LLM",         "metadata": {           "model": "gpt-4"         }       }     ],     "nextCursor": "cursor_for_pagination"   }"""
        return await self.proxy.call_tool('phoenix', 'get-span-annotations', kwargs)

    async def list_sessions(self, **kwargs) -> Any:
        """List sessions for a project.  Sessions represent conversation flows grouped across traces.  Example usage:   Show me the last 10 sessions for project "default"  Expected return:   Array of session objects ordered by the requested sort order."""
        return await self.proxy.call_tool('phoenix', 'list-sessions', kwargs)

    async def get_session(self, **kwargs) -> Any:
        """Get a single session by GlobalID or user-provided session_id.  Example usage:   Show me session "chat-123"  Expected return:   A session object and, optionally, its annotations."""
        return await self.proxy.call_tool('phoenix', 'get-session', kwargs)

    async def list_annotation_configs(self, **kwargs) -> Any:
        """List Phoenix annotation configs.  Annotation configs define the available human or automated labels, scores, and freeform annotation types.  Example usage:   Show me all annotation configs  Expected return:   Array of annotation config objects."""
        return await self.proxy.call_tool('phoenix', 'list-annotation-configs', kwargs)

    async def phoenix_support(self, **kwargs) -> Any:
        """Get help with Phoenix and OpenInference.  - Tracing AI applications via OpenInference and OpenTelemetry - Phoenix datasets, experiments, and prompt management - Phoenix evals and annotations  Use this tool when you need assistance with Phoenix features, troubleshooting, or best practices.  Expected return:   Expert guidance about how to use and integrate Phoenix"""
        return await self.proxy.call_tool('phoenix', 'phoenix-support', kwargs)
