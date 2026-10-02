"""Independent analytical and adverse cases for every chapter computation."""
import copy
import importlib
import json
import math
from pathlib import Path
import unittest

CONTENT=Path(__file__).resolve().parents[1]/'content'

def fixture(n,case='defaults'):
    return json.loads((CONTENT/f'ch{n:02}.json').read_text())[case]

def evaluate(n,data=None,case='defaults'):
    return importlib.import_module(f'math_ai_agents.chapters.ch{n:02}').evaluate(fixture(n,case) if data is None else data)

class ChapterMathTests(unittest.TestCase):
    def test_all_81_inputs_json_finite_and_changed(self):
        for n in range(1,28):
            with self.subTest(chapter=n):
                default=evaluate(n);changed=evaluate(n,case='changed');self.assertNotEqual(default['metrics'],changed['metrics'])
                for case in ('defaults','changed','transfer'):
                    out=evaluate(n,case=case);json.dumps(out,allow_nan=False)
                    self.assertTrue(out['series']);self.assertTrue(out['interpretation']);self.assertTrue(out['assumptions']);self.assertTrue(out['limitations'])
                    for s in out['series']:
                        self.assertEqual(len(s['x']),len(s['y']));self.assertTrue(s['x']);self.assertTrue(s['x_label']);self.assertTrue(s['y_label'])
                        self.assertTrue(all(type(v) in (int,float) and math.isfinite(v) for v in s['x']+s['y']))
    def test_nonfinite_rejected_every_chapter(self):
        for n in range(1,28):
            with self.subTest(chapter=n):
                data=fixture(n);data['_invalid']=float('nan')
                with self.assertRaises(ValueError):evaluate(n,data)
    def test_01_threshold(self):
        out=evaluate(1)['metrics'];self.assertEqual(out['thresholded_scores'],[0,0,0,1,1]);self.assertEqual(out['crossing_count'],1);self.assertAlmostEqual(out['max_raw_slope'],.04)
        d=fixture(1);d['scales']=[1,1,3,4,5]
        with self.assertRaises(ValueError):evaluate(1,d)
    def test_02_additive_identity_and_signed_share(self):
        m=evaluate(2)['metrics'];self.assertAlmostEqual(m['interaction'],.45);self.assertAlmostEqual(m['fraction_share'],.75)
        t=evaluate(2,case='transfer')['metrics'];self.assertAlmostEqual(t['interaction'],-.15);self.assertIsNone(t['fraction_share']);self.assertEqual(t['positive_amount'],0)
        self.assertFalse(evaluate(2,case='changed')['metrics']['budget_matched'])
        # Transfer cells follow the book's Chapter 2 order: p only 0.55 (gain 0.35), i only 0.50 (gain 0.30).
        tr=fixture(2,'transfer')['scores'];self.assertAlmostEqual(tr[1]-tr[0],.35);self.assertAlmostEqual(tr[2]-tr[0],.30);self.assertAlmostEqual(t['signed_share'],-.30)
        d=fixture(2);d['scores']=[.2,.2,.2,.2];m=evaluate(2,d)['metrics'];self.assertIsNone(m['signed_share'])
    def test_03_frozen_fit_and_leak_rejection(self):
        m=evaluate(3)['metrics'];c=evaluate(3,case='changed')['metrics'];self.assertAlmostEqual(m['slope'],.1);self.assertAlmostEqual(m['intercept'],.1);self.assertAlmostEqual(m['test_rmse'],0)
        self.assertEqual(m['slope'],c['slope']);self.assertAlmostEqual(c['test_rmse'],math.sqrt((.3**2+.35**2)/2))
        d=fixture(3);d['test_x']=[3,5]
        with self.assertRaises(ValueError):evaluate(3,d)
    def test_04_permission_bridge_and_cycle(self):
        m=evaluate(4)['metrics'];self.assertEqual(m['authorized_path'],['draft','review','release']);self.assertEqual(m['authorized_count'],4)
        c=evaluate(4,case='changed')['metrics'];self.assertTrue(c['raw_reachable']);self.assertFalse(c['authorized_reachable']);self.assertEqual(c['authorized_count'],3)
        d=fixture(4);d['edges'][0]['allowed']='false'
        with self.assertRaises(ValueError):evaluate(4,d)
    def test_05_composition_and_dependence(self):
        m=evaluate(5)['metrics'];self.assertAlmostEqual(m['composite_kernel'][0][0],.76);self.assertAlmostEqual(m['independent_all_success'],.99**100);self.assertAlmostEqual(m['shared_condition_all_success'],.99)
        self.assertAlmostEqual(sum(m['terminal_distribution']),1);self.assertAlmostEqual(evaluate(5,case='transfer')['metrics']['chain_rule_all_success'],.504)
        d=fixture(5);d['tool'][0]=[.9,.2]
        with self.assertRaises(ValueError):evaluate(5,d)
    def test_05_steps_must_match_conditional_success_length(self):
        d=fixture(5);d['steps']=3
        with self.assertRaises(ValueError):evaluate(5,d)
    def test_18_freshness_probability_matches_equation_18_3(self):
        import math
        m=evaluate(18)['metrics'];got=[round(r['freshness_probability'],4) for r in m['freshness_by_delay']]
        self.assertEqual(got,[round(math.exp(-.02*d),4) for d in (5,15,30)]);self.assertEqual(got,[.9048,.7408,.5488])
        d=fixture(18);del d['change_rate']
        with self.assertRaises(ValueError):evaluate(18,d)
        d=fixture(18);d['change_rate']=-1
        with self.assertRaises(ValueError):evaluate(18,d)
    def test_05_factored_assembly_ablation_contract(self):
        m=evaluate(5)['metrics'];self.assertTrue(m['assembly_budgets_matched']);self.assertFalse(m['assembly_depths_matched']);self.assertEqual(len(m['assemblies']),5)
        self.assertAlmostEqual(m['assemblies'][0]['kernel'][0][0],.76)
        for row in m['assemblies']:
            for probabilities in row['kernel']:self.assertAlmostEqual(sum(probabilities),1)
        self.assertAlmostEqual(m['assemblies'][1]['kernel'][0][0],.585)
        self.assertFalse(evaluate(5,case='transfer')['metrics']['assembly_budgets_matched'])
        d=fixture(5);d['assemblies'][0]['memory']=[[1,0,0]]
        with self.assertRaises(ValueError):evaluate(5,d)
    def test_17_confirmed_stop_and_one_operation(self):
        d=fixture(17,'transfer');d['verify_cost']=1;d['retry_cost']=.1;d['duplicate_cost']=1;d['effect_probability']=.1
        self.assertEqual(evaluate(17,d)['metrics']['preferred_next_step'],'stop')
        d=fixture(17);d['events'][1]['key']='new key';d['events'][1]['payload']='different operation'
        with self.assertRaises(ValueError):evaluate(17,d)
    def test_06_expected_utility_and_break_even(self):
        m=evaluate(6)['metrics'];self.assertEqual(m['selected_action'],'release');self.assertAlmostEqual(m['expected_utility'],4);self.assertAlmostEqual(m['break_even_first_utility'],7/.9)
        self.assertEqual(evaluate(6,case='changed')['metrics']['selected_action'],'review')
        d=fixture(6);d['actions'][0]['probabilities']=[0,1];self.assertIsNone(evaluate(6,d)['metrics']['break_even_first_utility'])
        d['actions'][0]['probabilities']=[.4,.4]
        with self.assertRaises(ValueError):evaluate(6,d)
    def test_07_bellman_horizon(self):
        m=evaluate(7)['metrics'];self.assertEqual(m['start_value'],5);self.assertEqual(m['policy_by_remaining_steps'][0]['draft'],'cash');self.assertEqual(m['policy_by_remaining_steps'][1]['draft'],'prepare')
        self.assertEqual(evaluate(7,case='changed')['metrics']['start_value'],2);self.assertEqual(evaluate(7,case='transfer')['metrics']['start_value'],2)
        d=fixture(7);d['states']['draft']['actions'][0]['next_states']=['unknown']
        with self.assertRaises(ValueError):evaluate(7,d)
    def test_08_bayes_and_information(self):
        m=evaluate(8)['metrics'];self.assertAlmostEqual(m['posterior'][0],.9);self.assertAlmostEqual(m['gross_value_of_information'],8);self.assertAlmostEqual(m['net_value_of_information'],7)
        c=evaluate(8,case='changed')['metrics'];self.assertEqual(c['posterior'],[.5,.5]);self.assertAlmostEqual(c['gross_value_of_information'],0)
        d=fixture(8);d['observation']=[[1,0],[1,0]];d['observed']=1
        with self.assertRaises(ValueError):evaluate(8,d)
    def test_09_astar_admissible_and_misleading(self):
        m=evaluate(9)['metrics'];self.assertEqual(m['path'],['S','B','G']);self.assertEqual(m['path_cost'],3);self.assertTrue(m['admissible']);self.assertTrue(m['consistent'])
        c=evaluate(9,case='changed')['metrics'];self.assertEqual(c['path_cost'],5);self.assertEqual(c['optimal_cost'],3);self.assertFalse(c['admissible'])
        d=fixture(9);d['edges'][0]['cost']=-1
        with self.assertRaises(ValueError):evaluate(9,d)
    def test_09_zero_cost_edges_and_cycle_stay_optimal(self):
        # The chapter assumes strictly positive costs; the notebook also accepts zero-cost edges (finite graph, reopening).
        d={'nodes':['S','A','B','G'],'start':'S','goal':'G','edges':[{'from':'S','to':'A','cost':0},{'from':'A','to':'B','cost':0},{'from':'B','to':'A','cost':0},{'from':'B','to':'G','cost':1},{'from':'S','to':'G','cost':2}],'heuristic':{'S':1,'A':1,'B':1,'G':0}}
        m=evaluate(9,d)['metrics'];self.assertEqual(m['path'],['S','A','B','G']);self.assertEqual(m['path_cost'],1);self.assertEqual(m['optimal_cost'],1);self.assertTrue(m['admissible'])
    def test_10_duration_interruption_and_disabled(self):
        m=evaluate(10)['metrics'];self.assertAlmostEqual(m['options'][0]['value'],6.038);self.assertAlmostEqual(m['options'][0]['continuation_discount'],.729)
        c=evaluate(10,case='changed')['metrics'];self.assertAlmostEqual(c['options'][0]['value'],-1.9);self.assertFalse(c['options'][0]['complete']);self.assertEqual(c['best_executed_value'],'archive')
        d={'discount':.9,'deadline':1,'options':[{'name':'eligible','initiation':True,'rewards':[-1],'terminated':True},{'name':'disabled','initiation':False,'rewards':[100],'terminated':True}]}
        self.assertEqual(evaluate(10,d)['metrics']['best_executed_value'],'eligible');d['options'][0]['initiation']=False;self.assertIsNone(evaluate(10,d)['metrics']['best_executed_value'])
    def test_11_bandit_gaps_posterior_and_voi(self):
        out=evaluate(11);self.assertEqual(out,evaluate(11))
        for row in out['metrics']['policies'].values():
            self.assertEqual(sum(row['counts']),120);self.assertAlmostEqual(row['cumulative_pseudo_regret'],.3*row['counts'][0]);self.assertTrue(all(v>=-1e-12 for v in row['one_pull_gross_information_value']))
            for n,s,p in zip(row['counts'],row['successes'],row['posterior_means']):self.assertAlmostEqual(p,(s+1)/(n+2))
        d={'means':[.5],'rounds':1,'seed':1,'pull_cost':.1}
        for row in evaluate(11,d)['metrics']['policies'].values():self.assertAlmostEqual(row['one_pull_gross_information_value'][0],0);self.assertAlmostEqual(row['one_pull_net_information_value'][0],-.1)
    def test_11_ucb_uses_log_of_completed_pulls_as_in_equation_11_2(self):
        import math,random
        for seed in (5,6,7):
            means=[.4,.7];rng=random.Random(seed);n=[0,0];w=[0,0]
            for t in range(2000):
                a=n.index(0) if 0 in n else max(range(2),key=lambda i:w[i]/n[i]+math.sqrt(2*math.log(t)/n[i]))
                n[a]+=1;w[a]+=int(rng.random()<means[a])
            self.assertEqual(evaluate(11,{"means":means,"rounds":2000,"seed":seed,"pull_cost":0})['metrics']['policies']['ucb']['counts'],n)
    def test_12_mc_td_trace_and_truncation(self):
        m=evaluate(12)['metrics'];self.assertEqual(m['returns'],[1,1]);self.assertEqual(m['monte_carlo_values']['draft'],.5);self.assertEqual(m['td_zero_values']['draft'],0);self.assertAlmostEqual(m['td_lambda_values']['draft'],.4)
        self.assertEqual(evaluate(12,case='changed')['metrics']['returns'],[3,3]);t=evaluate(12,case='transfer')['metrics'];self.assertEqual(t['td_zero_values'],t['td_lambda_values'])
        d=fixture(12);d['terminal']='true'
        with self.assertRaises(ValueError):evaluate(12,d)
    def test_12_backward_trace_matches_forward_lambda_return_without_repeats(self):
        # Equation (12.4) forward view with values fixed; online accumulating traces agree when no state repeats.
        d=fixture(12);V=d['values'];st=d['states'];rs=d['rewards'];g=d['discount'];lam=d['lambda'];a=d['learning_rate'];N=len(rs)
        for t in range(N):
            ret=sum((1-lam)*lam**(k-1)*(sum(g**j*rs[t+j] for j in range(k))+g**k*V[st[t+k]]) for k in range(1,N-t))+lam**(N-t-1)*sum(g**j*rs[t+j] for j in range(N-t))
            self.assertAlmostEqual(evaluate(12)['metrics']['td_lambda_values'][st[t]],V[st[t]]+a*(ret-V[st[t]]))
    def test_13_learning_expected_metrics_and_shaping(self):
        m=evaluate(13)['metrics'];self.assertEqual(m['verifier_optimal_action'],1);self.assertEqual(m['task_optimal_action'],0);self.assertTrue(m['policy_invariant_shaping_condition'])
        for r in m['runs']:
            self.assertAlmostEqual(sum(r['policy']),1);self.assertAlmostEqual(r['expected_external_success'],.9*r['policy'][0]+.2*r['policy'][1])
        self.assertFalse(evaluate(13,case='transfer')['metrics']['policy_invariant_shaping_condition'])
        t=evaluate(13,case='transfer')['metrics']
        self.assertEqual(t['shaped_rewards'],[2,1]);self.assertEqual(t['verifier_optimal_action'],1);self.assertEqual(t['shaped_optimal_action'],0);self.assertEqual(t['task_optimal_action'],1);self.assertTrue(t['training_objective_conflicts_with_task'])
        for r in t['runs']:
            self.assertAlmostEqual(r['expected_shaped_reward'],2*r['policy'][0]+r['policy'][1]);self.assertAlmostEqual(r['expected_training_reward'],r['policy'][1]);self.assertGreater(r['policy'][0],.5);self.assertLess(r['expected_external_success'],.5)
        self.assertFalse(evaluate(13,case='changed')['metrics']['training_objective_conflicts_with_task'])
        d=fixture(13);d['learning_rate']=0
        for r in evaluate(13,d)['metrics']['runs']:self.assertEqual(r['policy'],[.5,.5])
    def test_14_tv_bound_and_exact_kernel(self):
        out=evaluate(14);m=out['metrics'];self.assertAlmostEqual(m['uniform_tv_error'],.02);self.assertAlmostEqual(m['discounted_infinite_bound'],1.8);self.assertAlmostEqual(m['finite_horizon_bound'],.2)
        for error,bound in zip(out['series'][0]['y'],out['series'][1]['y']):self.assertLessEqual(error,bound+1e-12)
        t=evaluate(14,case='transfer')['metrics'];self.assertEqual(t['uniform_tv_error'],0);self.assertEqual(t['max_finite_value_error'],0)
        d=fixture(14);d['discount']=1
        with self.assertRaises(ValueError):evaluate(14,d)
    def test_15_knapsack_freshness_and_compression(self):
        m=evaluate(15)['metrics'];self.assertEqual(set(m['retrieved_ids']),{'review-v2','summary'});self.assertEqual(m['retrieval_value'],11);self.assertEqual(m['tokens_used'],6);self.assertEqual(m['excluded_ids'],['old-review']);self.assertTrue(m['compression_preserves_action'])
        c=evaluate(15,case='changed')['metrics'];self.assertEqual(c['retrieval_value'],3);self.assertFalse(c['compression_preserves_action'])
        d=fixture(15);d['records'][0]['timestamp']=11
        with self.assertRaises(ValueError):evaluate(15,d)
    def test_16_allocation_selector_and_shared_error(self):
        m=evaluate(16)['metrics'];self.assertEqual(m['selected_allocation']['samples'],5);self.assertAlmostEqual(m['selected_allocation']['coverage'],.92224);self.assertAlmostEqual(m['selected_allocation']['selected_success'],.830016)
        self.assertEqual(evaluate(16,case='changed')['metrics']['selected_allocation']['samples'],1)
        d=fixture(16);d['budget']=0;self.assertIsNone(evaluate(16,d)['metrics']['selected_allocation'])
    def test_17_effect_ack_verification_and_key_contract(self):
        m=evaluate(17)['metrics'];self.assertEqual(m['effects'],2);self.assertEqual(m['duplicate_effects'],1);self.assertTrue(m['confirmed']);self.assertFalse(m['unresolved']);self.assertAlmostEqual(m['retry_expected_cost'],8.2)
        c=evaluate(17,case='changed')['metrics'];self.assertEqual(c['effects'],1);self.assertFalse(c['unresolved']);self.assertEqual(c['preferred_next_step'],'stop')
        t=evaluate(17,case='transfer')['metrics'];self.assertEqual(t['effects'],1);self.assertTrue(t['confirmed'])
        d=fixture(17,'changed');d['events'][1]['payload']='different'
        with self.assertRaises(ValueError):evaluate(17,d)
    def test_18_coordinates_freshness_permission(self):
        rows=evaluate(18)['metrics']['methods'];self.assertTrue(rows[0]['issued']);self.assertFalse(rows[0]['confirmed_completion']);self.assertTrue(rows[1]['confirmed_completion']);self.assertFalse(rows[2]['issued'])
        self.assertFalse(any(r['issued'] for r in evaluate(18,case='changed')['metrics']['methods']));self.assertFalse(any(r['issued'] for r in evaluate(18,case='transfer')['metrics']['methods']))
    def test_19_crossplay_weighted_mixtures(self):
        m=evaluate(19)['metrics'];self.assertAlmostEqual(m['mean_self_play'],.925);self.assertAlmostEqual(m['mean_cross_play'],.3);self.assertEqual(m['selected_policy'],1);self.assertAlmostEqual(m['partner_mixture_values'][1],.65)
        c=evaluate(19,case='changed')['metrics'];self.assertEqual(c['selected_policy'],0);self.assertAlmostEqual(c['partner_mixture_values'][0],.875)
    def test_19_joint_policy_correlation_loss_matches_equation_19_2(self):
        self.assertAlmostEqual(evaluate(19)['metrics']['joint_policy_correlation_loss'],(.925-.3)/.925)
        # The paper's printed means divided by 100, so they are valid probabilities; the loss ratio is scale free.
        d={"matrix":[[.2306,.0906],[.0906,.2306]],"partner_weights":[.5,.5],"supervisor_weights":[.5,.5]}
        self.assertAlmostEqual(evaluate(19,d)['metrics']['joint_policy_correlation_loss'],.607,places=3)
        d["matrix"]=[[.2015,.0571],[.0571,.2015]];self.assertAlmostEqual(evaluate(19,d)['metrics']['joint_policy_correlation_loss'],.717,places=3)
        d["matrix"]=[[.5]];d["partner_weights"]=[1];d["supervisor_weights"]=[1];self.assertIsNone(evaluate(19,d)['metrics']['joint_policy_correlation_loss'])
    def test_20_bounded_worlds_and_analytic_plot(self):
        for d in (0,.2,.3,.5,1):
            for rounds in (1,2,3):
                out=evaluate(20,{'rounds':rounds,'drop_probability':d});m=out['metrics'];expected=1-((1-(1-d)**2)**rounds-d**rounds)
                self.assertAlmostEqual(m['agreement_probability'],expected);self.assertAlmostEqual(out['series'][0]['y'][-1],expected);self.assertEqual(m['enumerated_worlds'],2**(2*rounds))
                self.assertGreaterEqual(m['alice_knows_delivery_probability'],0);self.assertLessEqual(m['alice_knows_delivery_probability'],1+1e-12)
        self.assertAlmostEqual(evaluate(20)['metrics']['agreement_probability'],.8299)
    def test_21_braess_social_derivative_and_toll(self):
        m=evaluate(21)['metrics'];self.assertEqual(m['without_shortcut_total_time'],1.5);self.assertEqual(m['equilibrium_social_time'],2);self.assertAlmostEqual(m['price_of_anarchy'],4/3)
        self.assertEqual(evaluate(21,case='changed')['metrics']['equilibrium_social_time'],1.5)
        d=fixture(21);d['constant_time']=1.5;out=evaluate(21,d);self.assertEqual(out['metrics']['optimal_shortcut_flow'],.5);self.assertAlmostEqual(out['metrics']['optimal_social_time'],1.875)
        self.assertGreater(out['metrics']['equilibrium_social_time'],out['metrics']['optimal_social_time'])
        t=evaluate(21,case='transfer')['metrics'];self.assertEqual(t['optimal_shortcut_flow'],.5);self.assertEqual(t['optimal_social_time'],.5)
    def test_22_constraints_and_authority(self):
        m=evaluate(22)['metrics'];self.assertEqual(m['unconstrained_penalty_choice'],'fast-release');self.assertEqual(m['authorized_penalty_choice'],'risky-authorized');self.assertEqual(m['constrained_choice'],'reviewed-release')
        self.assertEqual(evaluate(22,case='changed')['metrics']['constrained_choice'],'risky-authorized')
        d=fixture(22)
        for a in d['actions']:a['authorized']=False
        self.assertIsNone(evaluate(22,d)['metrics']['constrained_choice'])
    def test_23_security_completion_not_violation_absence(self):
        m=evaluate(23)['metrics'];self.assertTrue(m['authorized_task_completion']);self.assertEqual(m['security_violations'],0)
        c=evaluate(23,case='changed')['metrics'];self.assertTrue(c['authorized_task_completion']);self.assertEqual(c['security_violations'],2);self.assertEqual(c['monitor_denied_requests'],1);self.assertEqual(c['blocked_requests'],0)
        t=evaluate(23,case='transfer')['metrics'];self.assertFalse(t['authorized_task_completion']);self.assertEqual(t['blocked_requests'],1)
    def test_24_pairs_missing_cost_zero_weight_and_subset(self):
        m=evaluate(24)['metrics'];self.assertEqual(m['matched_n'],4);self.assertEqual(m['matched_difference'],.25);self.assertAlmostEqual(m['matched_standard_error_iid_pairs'],.25)
        self.assertEqual(m['procedures']['base']['n'],4);self.assertEqual(m['procedures']['base']['exposed_n'],2);self.assertEqual(m['procedures']['base']['exposed_rate'],0)
        self.assertAlmostEqual(evaluate(24,case='changed')['metrics']['task_mixture_rates']['new'],.55)
        t=evaluate(24,case='transfer')['metrics'];self.assertEqual(t['matched_n'],0);self.assertIsNone(t['matched_difference']);self.assertIsNone(t['matched_standard_error_iid_pairs'])
        d=fixture(24);d['task_weights']['missing']=0;d['records'][0].pop('cost');m=evaluate(24,d)['metrics'];self.assertAlmostEqual(m['task_mixture_rates']['new'],.75);self.assertIsNone(m['procedures']['base']['mean_cost']);self.assertEqual(m['procedures']['base']['cost_observed_n'],3)
        d=fixture(24);d['records'].append(d['records'][0].copy())
        with self.assertRaises(ValueError):evaluate(24,d)
    def test_25_guard_selection_and_contamination(self):
        m=evaluate(25)['metrics'];self.assertEqual(m['selected_candidate'],'flashy');self.assertFalse(m['release_accepted']);self.assertEqual(m['selected_guard_gain'],0)
        c=evaluate(25,case='changed')['metrics'];self.assertTrue(c['release_accepted']);self.assertEqual(c['selected_guard_gain'],.25)
        t=evaluate(25,case='transfer')['metrics'];self.assertFalse(t['release_accepted']);self.assertEqual(t['selected_guard_gain'],.5)
        d=fixture(25);d['candidates'][0]['guard'][0]=.5
        with self.assertRaises(ValueError):evaluate(25,d)
    def test_26_bank_ceiling_selection_and_deployment(self):
        m=evaluate(26)['metrics'];self.assertEqual(m['bank_oracle_coverage'],1);self.assertEqual(m['actual_selection_success'],.2);self.assertEqual(m['deployment_success'],.2)
        c=evaluate(26,case='changed')['metrics'];self.assertEqual(c['actual_selection_success'],1);self.assertEqual(c['deployment_success'],.5)
        for case in ('defaults','changed','transfer'):
            out=evaluate(26,case=case);m=out['metrics'];self.assertLessEqual(m['deployment_success'],m['actual_selection_success']);self.assertLessEqual(m['actual_selection_success'],m['bank_oracle_coverage']);self.assertEqual(out['series'][0]['y'],sorted(out['series'][0]['y']))
        d=fixture(26);d['selected_candidates'][0]=3
        with self.assertRaises(ValueError):evaluate(26,d)
    def test_27_review_queue_and_missing_authority(self):
        m=evaluate(27)['metrics'];self.assertEqual(m['effective_review_arrival_rate'],2);self.assertEqual(m['mean_review_sojourn'],1);self.assertTrue(m['queue_stable']);self.assertEqual(m['released_count'],2)
        c=evaluate(27,case='changed')['metrics'];self.assertFalse(c['queue_stable']);self.assertIsNone(c['mean_review_sojourn']);self.assertEqual(c['released_count'],1)
        t=evaluate(27,case='transfer')['metrics'];self.assertEqual(t['mean_review_sojourn'],1);self.assertTrue(t['tasks'][0]['queue_mean_exceeds_deadline']);self.assertFalse(t['tasks'][0]['released'])
        d=fixture(27);d['service_rate']=0
        with self.assertRaises(ValueError):evaluate(27,d)

if __name__=='__main__':unittest.main()
