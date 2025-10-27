export interface MutationMapper<
    FrontendRequest,
    BackendRequest,
    BackendResponse,
    FrontendResponse,
> {
    toRequest(inp: FrontendRequest): BackendRequest
    fromResponse(out: BackendResponse): FrontendResponse
}

export interface QueryMapper<
    BackendResponse,
    FrontendResponse
> {
    fromResponse(out: BackendResponse): FrontendResponse
}
