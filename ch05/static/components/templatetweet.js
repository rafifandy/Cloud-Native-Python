export default class Tweettemplate extends React.Component {
  render(){
    return(
      <li className="collection-item avatar">
        <i className="material-icons circle red">play_arrow</i>
        <span className="title">{this.props.username}</span>
        <p>{this.props.body}</p>
        <p>{this.props.id}</p>
      </li>
      );
    }
}
