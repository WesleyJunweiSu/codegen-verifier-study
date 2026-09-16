"""Resume completed generation through public selection then frozen scoring."""
import json
import continue_confirmation as flow
from freeze_matched_score import RUN


def main():
    run=flow.ROOT/'runs'/RUN;flow.JOURNAL=run/'continuation-state.json'
    state=json.loads(flow.JOURNAL.read_text()) if flow.JOURNAL.exists() else {'jobs':{}}
    if state.get('stage')=='complete':print('Already complete');return
    source=flow.git('rev-parse','HEAD')
    flow.workflow(state,'matched_visible','matched-visible.yml',RUN,'visible-evidence',run/'visible',source)
    flow.python('freeze_matched_score.py')
    source=flow.commit([str(run.relative_to(flow.ROOT))],'Freeze matched-budget development decisions before scoring')
    flow.workflow(state,'matched_score','score-frozen.yml',RUN,'frozen-scoring',run/'linux',source)
    flow.python('analyze_matched_budget.py')
    flow.checkpoint(state,'complete')
    flow.commit([str(run.relative_to(flow.ROOT))],'Record full matched-budget development comparison')


if __name__=='__main__':main()
